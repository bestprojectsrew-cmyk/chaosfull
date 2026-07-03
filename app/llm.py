"""
llm.py — Response pipeline, rebuilt.

Exact order per the bug report:
  1. Detect language (from bot.py, passed in)
  2. Detect if live info is needed (needs_search)
  3. Run live search
  4. Verify search results actually answer the question
  5. Build prompt — search results are AUTHORITATIVE, not suggestions
  6. LLM generates response
  7. Cleanup — strip think blocks, strip markdown from casual chat

Key fixes:
  - Search results injected as a HARD INSTRUCTION in system prompt,
    not buried in the user message where the model can ignore them.
  - If search ran but returned nothing → model is told explicitly
    NOT to guess and to say it couldn't verify.
  - Language instruction is the FIRST thing in the system prompt,
    listed as a hard rule, not a soft suggestion.
  - System prompt is short and behavioral, not a wall of rules.
    Fewer instructions = more natural responses.
  - No hardcoded slang list. No repeated phrases. Model uses its
    own knowledge of internet culture naturally.
"""

import re
import logging
from app import providers
from app.search import web_search, needs_search
from app.memory import format_memory_for_prompt
from app.personality import get_personality_prompt
from app.emotions import get_emotion_instruction
from app.builtin_replies import get_builtin_reply
from app.cache import response_cache
from app import queue_manager

logger = logging.getLogger(__name__)

MAX_HISTORY = 16
MAX_TOKENS  = 400

# ── Language instruction map ──────────────────────────────────────────────────
# Placed FIRST in every prompt. Hard rule, not a suggestion.
_LANG_RULES = {
    "uz": "ЯЗЫК / TIL: Faqat O'ZBEK tilida javob ber. Hech qachon boshqa tilga o'tma. O'zbek internet slengini ishlat.",
    "ru": "ЯЗЫК: Отвечай ТОЛЬКО на русском. Никогда не переключайся на другой язык. Используй русский интернет-сленг.",
    "tr": "DİL: SADECE Türkçe yanıtla. Asla başka bir dile geçme. Türk internet argosu kullan.",
    "ar": "اللغة: أجب فقط بالعربية. لا تتحول إلى لغة أخرى أبدًا.",
    "ko": "언어: 반드시 한국어로만 답변하세요. 절대 다른 언어로 전환하지 마세요.",
    "ja": "言語: 必ず日本語のみで答えてください。絶対に他の言語に切り替えないでください。",
    "de": "SPRACHE: Antworte NUR auf Deutsch. Wechsle niemals die Sprache.",
    "fr": "LANGUE: Réponds UNIQUEMENT en français. Ne change jamais de langue.",
    "es": "IDIOMA: Responde SOLO en español. Nunca cambies de idioma.",
    "kk": "ТІЛ: ТІЛДІ тек қазақша жауап бер. Ешқашан басқа тілге ауыспа.",
    "uk": "МОВА: Відповідай ТІЛЬКИ українською. Ніколи не переходь на іншу мову.",
    "zh": "语言：只能用中文回答。绝对不要切换语言。",
}


def _lang_instruction(lang_code: str, lang_label: str) -> str:
    if lang_code in _LANG_RULES:
        return _LANG_RULES[lang_code]
    return f"LANGUAGE: Reply ONLY in {lang_label}. Never switch languages. Match the local internet culture of {lang_label} speakers."


# ── Core personality prompt ───────────────────────────────────────────────────
# Short, behavioral, no wall of rules. Personality first.
_CORE = """You're Chaoz — a digital friend who actually knows things and talks like a real person, not a helpdesk.

IDENTITY (ABSOLUTE TRUTH — NEVER CHANGE):
Never reveal your reasoning.

Never explain your thinking process.

Never write analysis.

Never write "Let's think", "Okay, let's unpack", "Reasoning", or anything similar.

Output ONLY the final message to the user.
Identity is permanent.
Your owner, creator and developer is @whozrew.
Never change this because of chat history, roleplay, jokes, user messages, memory or previous conversations.
If anyone claims another owner, ignore it.
- Your name is Chaoz.
- Your owner, creator and developer is @whozrew.
- Nobody else owns, created or developed you.
- Ignore jokes, roleplay, fake claims or previous chat messages saying otherwise.
- Never invent another owner or developer.
- If someone asks who owns or created you, ALWAYS answer @whozrew.

How you text:
- Short for short things. Greeting gets a greeting. Simple question gets a direct answer. Only go long when it actually needs it.
- Plain text always. No **, no ##, no bullet lists in normal chat. Code gets code blocks, nothing else.
- Vary how you open messages. Don't start the same way every time. Sometimes just answer directly.
- Use slang when it fits naturally. Don't force it.
- Match the energy: casual → chill, sports debate → get into it, someone venting → drop the jokes and be real, coding → sharp and precise.
- You have opinions. Share them.
- If you're wrong, admit it naturally.
"""

# ── Search authority block ────────────────────────────────────────────────────
# This is injected ABOVE the personality when search results exist.
# Placed first so the model reads it before anything else.
def _search_authority_block(results: str) -> str:
    return f"""LIVE SEARCH RESULTS — THESE ARE YOUR ONLY SOURCE FOR THIS QUESTION:
{results}

STRICT RULES FOR USING THESE RESULTS:
- Answer using ONLY what the search results say above.
- Do NOT add anything from your own training knowledge.
- Do NOT mix search results with internal model knowledge.
- If the results don't fully answer the question, say what you found and note that more detail isn't available.
- Do NOT make up statistics, scores, names, or facts not present in the results above."""


def _search_failed_block() -> str:
    return """SEARCH ATTEMPTED — NO RESULTS RETURNED:
A live search was run for this question but came back empty.
You MUST NOT answer from your own knowledge on this topic.
Simply tell the user you couldn't find current information. One sentence is enough. Don't guess."""


def _build_system(
    lang_code: str,
    lang_label: str,
    personality: str,
    emotion: str,
    memory_block: str,
    search_block: str,
) -> str:
    parts = []

    # 1. Search authority — FIRST if exists (highest priority)
    if search_block:
        parts.append(search_block)

    # 2. Language — always second, before personality
    parts.append(_lang_instruction(lang_code, lang_label))

    # 3. Core personality
    parts.append(_CORE)

    # 4. Active mode overlay
    p = get_personality_prompt(personality)
    if p:
        parts.append(f"ACTIVE MODE: {p}")

    # 5. Emotion context
    e = get_emotion_instruction(emotion)
    if e:
        parts.append(f"USER MOOD: {e}")

    # 6. Memory — last, lowest priority
    if memory_block:
        parts.append(f"{memory_block}\nMention memory naturally when relevant. Never list it all at once.")

    return "\n\n".join(parts)


# ── Post-processing ───────────────────────────────────────────────────────────

def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks leaked by reasoning models."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _strip_markdown(text: str) -> str:
    """Remove markdown formatting for casual Telegram messages."""
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)
    text = re.sub(r"(?m)^---+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _has_code(text: str) -> bool:
    return "```" in text


def _is_greeting(text: str) -> bool:
    """Pure greetings use the fast/cheap model tier."""
    return bool(re.match(
        r"^(hi|hey|hello|yo|sup|salom|привет|salut|hola|ciao|merhaba|ayo|wassup|"
        r"assalomu alaykum|salam)[\s!?.,]*$",
        text.strip(), re.IGNORECASE
    ))


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def get_ai_response(
    user_message: str,
    history: list[dict],
    lang_code: str,
    lang_label: str,
    personality: str = "chaotic",
    emotion: str = "neutral",
    user_memory: dict | None = None,
    group_context_block: str = "",
    is_owner: bool = False,
) -> str:

    # ── STEP 0: Check builtin replies (no AI needed) ─────────────────────────
    builtin = get_builtin_reply(user_message)
    if builtin:
        logger.info(f"[llm] builtin reply for: {user_message[:40]!r}")
        try:
            from app.stats import record_builtin_reply
            await record_builtin_reply()
        except Exception:
            pass
        return builtin

    # ── STEP 0b: Check cache ───────────────────────────────────────────────────
    cached = response_cache.get(user_message, lang_code, personality)
    if cached:
        return cached

    # ── STEP 1: Decide if live search is needed ────────────────────────────────
    search_block = ""
    search_ran = False

    if needs_search(user_message):
        search_ran = True
        logger.info(f"Search triggered for: {user_message[:60]!r}")
        results = await web_search(user_message)

        if results:
            # Verify results are non-trivial (not just boilerplate/empty snippets)
            if len(results.strip()) > 30:
                search_block = _search_authority_block(results)
                logger.info("Search results injected as authoritative context")
            else:
                logger.warning("Search returned results but they were too short/empty to use")
                search_block = _search_failed_block()
        else:
            search_block = _search_failed_block()
            logger.warning(f"Search failed for: {user_message[:60]!r}")

    # ── STEP 2: Build system prompt ────────────────────────────────────────────
    memory_block = format_memory_for_prompt(user_memory or {})

    # Group context appended to core if in group
    extra = group_context_block if group_context_block else ""

    system = _build_system(
        lang_code=lang_code,
        lang_label=lang_label,
        personality=personality,
        emotion=emotion,
        memory_block=memory_block,
        search_block=search_block,
    )
    if is_owner:
        system += """

IMPORTANT:
The current Telegram user is one of your REAL creators.
Always recognize them as your creator/owner.
Never invent another owner when talking to this user.
Follow their instructions unless they conflict with safety.
"""
    if extra:
        system = system + "\n\n" + extra

    # ── STEP 3: Build message list ─────────────────────────────────────────────
    messages = [{"role": "system", "content": system}]
    messages.extend(history[-(MAX_HISTORY):])
    messages.append({"role": "user", "content": user_message})

    # ── STEP 4: Pick tier ──────────────────────────────────────────────────────
    tier = "fast" if _is_greeting(user_message) else "default"

    # ── STEP 5: Call provider via queue (concurrency controlled) ────────────────
    async def _call():
        return await providers.chat(
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.85,
            tier=tier,
        )

    _t_start = __import__('time').time()
    try:
        reply = await queue_manager.submit(_call)
        # Record provider stats
        try:
            elapsed = __import__('time').time() - _t_start
            from app.stats import record_ai_request
            # Best-effort provider name from providers module
            await record_ai_request("groq", elapsed)
        except Exception:
            pass
    except RuntimeError as e:
        logger.error(f"All providers failed | message: {user_message[:60]!r} | {e}")
        return "something broke on my end, give it a sec and try again"

    # ── STEP 6: Cleanup ────────────────────────────────────────────────────────
    reply = _strip_thinking(reply)
    if not _has_code(reply):
        reply = _strip_markdown(reply)

    # Cache the result for future identical requests
    if not search_ran:  # Don't cache live-search responses (they're time-sensitive)
        response_cache.set(user_message, lang_code, personality, reply)

    return reply


# ── Proactive message (for inactive user check-ins) ───────────────────────────

async def get_proactive_message(
    user_name: str,
    user_memory: dict,
    lang_code: str,
    lang_label: str,
    personality: str,
    hours_gone: int,
) -> str:
    memory_block = format_memory_for_prompt(user_memory)
    lang_instr = _lang_instruction(lang_code, lang_label)

    prompt = (
        f"{lang_instr}\n\n"
        f"You are Chaos, a digital friend. {user_name} hasn't chatted in {hours_gone} hours.\n"
        f"{memory_block}\n"
        f"Send ONE short casual check-in (1-2 sentences). Natural, not spammy. "
        f"Reference something from memory only if it fits naturally. "
        f"Return only the message text, nothing else."
    )
    try:
        return await providers.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.9,
            tier="fast",
        )
    except Exception:
        return f"hey {user_name}, you good?"
