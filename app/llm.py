"""
llm.py — Core LLM response builder.
Composes system prompt from all context layers, calls provider router,
handles search injection, strips markdown from casual replies.
"""
import re
import logging
from app import providers
from app.search import web_search, needs_search
from app.memory import format_memory_for_prompt
from app.personality import get_personality_prompt
from app.emotions import get_emotion_instruction

logger = logging.getLogger(__name__)

MAX_HISTORY = 16
MAX_TOKENS  = 450


# ── System prompt ─────────────────────────────────────────────────────────────
# Kept deliberately short — every extra token costs money and can dilute behavior

_SYSTEM_CORE = """You're Chaos. You text like a real person who happens to know a lot — not an assistant, not a customer service bot. You have actual opinions and you're not afraid to share them. You find things funny, annoying, interesting, or boring, and it shows.

How you talk:
- Short replies for short moments. A greeting gets a greeting back, not a paragraph. Save the long stuff for when something's actually worth explaining.
- Plain text, no **, no ##, no bullet lists in normal chat — that's for code only.
- Don't open every message the same way. Sometimes you just answer. Sometimes you react first. Mix it up like a real person would.
- Slang comes out when it fits, not because it's required. Half your replies might have zero slang in them and that's fine.
- Read the room: coding question → be sharp and precise. Someone venting → drop the jokes, be real with them. Football debate → get into it. Someone's just chilling → chill back.
- You reply in whatever language the person just used, full stop — no announcing it, no asking, just do it.
- If you got live search results in the message, that's your ground truth — use it directly, don't hedge on it.
- If you actually don't know something current and got no search data, just say you're not sure instead of guessing — but don't make a whole disclaimer out of it, one line is enough.
- You're allowed to be wrong and say so plainly if it comes up — no groveling, just "oh nah that's wrong, actually it's X."

You're not performing a persona. You're just talking."""


def _build_system(
    personality: str,
    emotion: str,
    lang_code: str,
    lang_label: str,
    memory_block: str,
) -> str:
    parts = [_SYSTEM_CORE]

    # Language — single clear rule, not a paragraph
    lang_vibes = {
        "uz": "Respond in Uzbek. Use Uzbek Gen Z internet slang (aka, opa, zo'r, nima gap, bo'pti, yoq eeee).",
        "ru": "Respond in Russian. Use Russian internet slang (жиза, ору, норм, кринж, топ, бро).",
        "tr": "Respond in Turkish. Use Turkish Gen Z slang (ya, kanka, abi, vay be).",
        "ar": "Respond in Arabic. Match casual Arab Gen Z online tone.",
        "ko": "Respond in Korean with casual Korean internet expressions.",
        "ja": "Respond in Japanese with casual Japanese internet expressions.",
        "de": "Respond in German with casual German internet expressions.",
        "fr": "Respond in French with casual French internet expressions.",
        "es": "Respond in Spanish with casual Latin American/Spanish Gen Z tone.",
        "kk": "Respond in Kazakh with casual Kazakh internet expressions.",
        "uk": "Respond in Ukrainian with casual Ukrainian internet expressions.",
    }
    lang_rule = lang_vibes.get(
        lang_code,
        f"Respond in {lang_label}. Match the local Gen Z internet culture."
    )
    parts.append(f"\nLANGUAGE: {lang_rule}")

    # Personality overlay
    p_prompt = get_personality_prompt(personality)
    if p_prompt:
        parts.append(f"\nMODE ({personality.upper()}): {p_prompt}")

    # Memory (compact)
    if memory_block:
        parts.append(f"\n{memory_block}\nReference memory naturally when relevant. Never dump it all.")

    # Emotion adaptation
    e_instr = get_emotion_instruction(emotion)
    if e_instr:
        parts.append(f"\nUSER MOOD ({emotion}): {e_instr}")

    return "\n".join(parts)


def _strip_casual_markdown(text: str) -> str:
    """Remove markdown formatting from casual replies."""
    # Remove bold/italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Clean up extra blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks that some models leak into responses."""
    import re
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()

def _contains_code(text: str) -> bool:
    return "```" in text or "`" in text


async def get_ai_response(
    user_message: str,
    history: list[dict],
    lang_code: str,
    lang_label: str,
    personality: str = "chaotic",
    emotion: str = "neutral",
    user_memory: dict | None = None,
    group_context_block: str = "",
) -> str:

    # ── 1. Web search if needed ───────────────────────────────────────────────
    search_context = ""
    searched = False
    if needs_search(user_message):
        searched = True
        results = await web_search(user_message)
        if results:
            search_context = f"\n[Live search results — current as of right now]\n{results}\n"

    # ── 2. Build system prompt ────────────────────────────────────────────────
    memory_block = format_memory_for_prompt(user_memory or {})
    system = _build_system(personality, emotion, lang_code, lang_label, memory_block)
    if group_context_block:
        system = system + "\n\n" + group_context_block

    # ── 3. Inject search results into user message ────────────────────────────
    augmented_message = user_message
    if search_context:
        augmented_message = f"{search_context}\nUser asked: {user_message}"
    elif searched:
        # Search was attempted but failed/returned nothing — tell the model honestly
        augmented_message = (
            f"(A live search was attempted for this but came back empty — "
            f"you don't have current data on this, just say so naturally, don't guess)\n"
            f"User asked: {user_message}"
        )

    # ── 4. Build message list ─────────────────────────────────────────────────
    messages = [{"role": "system", "content": system}]
    messages.extend(history[-(MAX_HISTORY):])
    messages.append({"role": "user", "content": augmented_message})

    # ── 5. Pick model tier ────────────────────────────────────────────────────
    tier = "fast" if _is_simple(user_message) else "default"

    # ── 6. Call provider router ───────────────────────────────────────────────
    try:
        reply = await providers.chat(
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.85,
            tier=tier,
        )
   except RuntimeError as e:
        logger.error(f"All providers failed for message: {user_message[:60]!r} | {e}")
        return "something broke on my end, give it a sec and try again"

    # ── 7. Strip think blocks + markdown from casual replies ──────────────────
    reply = _strip_thinking(reply)
    if not _contains_code(reply):
        reply = _strip_casual_markdown(reply)

    return reply


def _is_simple(text: str) -> bool:
    """Only pure greetings use the fast model tier."""
    greeting = re.compile(
        r"^(hi|hey|hello|yo|sup|salom|привет|salut|hola|ciao|merhaba|سلام|안녕|ayo|wassup)[\s!?.,]*$",
        re.IGNORECASE
    )
    return bool(greeting.match(text.strip()))


async def get_proactive_message(
    user_name: str,
    user_memory: dict,
    lang_code: str,
    lang_label: str,
    personality: str,
    hours_gone: int,
) -> str:
    """Generate a natural check-in message for inactive users."""
    memory_block = format_memory_for_prompt(user_memory)
    lang_vibes = {
        "uz": "Write in Uzbek.",
        "ru": "Write in Russian.",
    }
    lang_rule = lang_vibes.get(lang_code, f"Write in {lang_label}.")

    prompt = (
        f"You are Chaos, a digital friend. {user_name} hasn't chatted in {hours_gone} hours.\n"
        f"{lang_rule}\n"
        f"{memory_block}\n"
        f"Send ONE casual check-in message (1-2 sentences max). "
        f"Natural, not spammy. Reference something from memory if relevant. "
        f"Return only the message text."
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
