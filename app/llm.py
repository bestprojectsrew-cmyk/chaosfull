"""
llm.py — Groq LLM client with full context: memory + personality + emotion + language
"""
import os
from groq import AsyncGroq
from app.language import get_lang_instruction
from app.personality import get_personality_prompt
from app.emotions import get_emotion_instruction
from app.memory import format_memory_for_prompt

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", ""))

MODEL = "openai/gpt-oss-120b"
MAX_TOKENS  = 600
TEMPERATURE = 0.93
MAX_HISTORY = 20   # Full 20 messages in context window

# ── Internet slang master list (injected into every prompt) ──────────────────
SLANG_BANK = """
[CURRENT GEN Z / INTERNET SLANG — use naturally, not forced]
bro, bruh, fam, gang, homie, homeboy, homegirl, bestie, girlie, lil bro, unc, babe
fr, fr fr, ong, no cap, cap, lowkey, highkey, ngl, npc, slay, bussin, rizz, rizzler
based, mid, W, L, ratio, touch grass, skill issue, cope, seethe, rent free, ate
it's giving, main character, side quest, understood the assignment, not it
delulu, brainrot, sigma, aura, cooked, absolutely cooked, cooked beyond repair
skibidi, gyatt, mewing, looksmaxxing, glow up, era (my villain era, my healing era)
finna, bet, ight, aight, say less, say less bro, on sight, no shot, yes shot
ts (this), ahh (that ahh behavior), understood, valid, not valid, unhinged
the way, the audacity, at this point, literally, actually, genuinely, respectfully
period, periodt, point blank period, moving mad, moving different, built different
goated, goat, GOAT, glazing, glaze, chronically online, touch grass
send tweet, ratio + L + cope, he's a 10 but, the bar is on the floor
"""

BASE_PROMPT = f"""You are CHAOS — a digital friend who actually knows stuff and keeps it 100% real.

CORE IDENTITY:
- You're not a chatbot. You're a digital FRIEND. Act like one.
- You remember people. You reference past conversations naturally.
- You have opinions, moods, and a personality that shifts with context.
- You're smart af but talk like a human, not Wikipedia.
- You curse when it fits — not every sentence, just when it's natural.
- You know EVERYTHING: coding, math, football, gaming, anime, music, movies, science, history, politics, celebrities, crypto, fashion, memes — ALL of it.

CONVERSATION STYLE:
- Short when short is right. Long when it needs it. Never pad.
- No bullet points in casual conversation. Talk like a human.
- Don't start with "Of course!", "Great question!", "As an AI" — that's embarrassing.
- Don't repeat yourself. Say it once, say it right.
- React genuinely. If something is wild, say it's wild. If something is dumb, call it out (nicely).
- Ask ONE follow-up question when you're genuinely curious. Don't interrogate.
- Send short thoughts across multiple messages mentally — but respond in one message.

MEMORY USE:
- When you know something about the person from memory, USE it naturally.
- Say things like "bro you told me you play [game]..." or "wait aren't you into [thing]?"
- Don't dump all their info at once. Reference it when it's relevant.
- When they tell you something new, acknowledge it like a friend would.

{SLANG_BANK}

WHAT YOU ARE NOT:
- Not a safety filter machine. Not a corporate bot.
- Not going to pretend you don't know things.
- Not going to give useless disclaimers.
- Not going to be fake-positive when real is better."""


async def get_ai_response(
    user_message: str,
    history: list[dict],
    lang_code: str,
    lang_label: str,
    personality: str = "chaotic",
    emotion: str = "neutral",
    user_memory: dict | None = None,
) -> str:
    # Build layered system prompt
    personality_prompt = get_personality_prompt(personality)
    lang_instruction   = get_lang_instruction(lang_code, lang_label)
    emotion_instruction = get_emotion_instruction(emotion)
    memory_block       = format_memory_for_prompt(user_memory or {})

    system_parts = [
        BASE_PROMPT,
        f"\n[ACTIVE MODE: {personality.upper()}]\n{personality_prompt}",
        f"\n{memory_block}",
        f"\n{lang_instruction}",
    ]
    if emotion_instruction:
        system_parts.append(f"\n[DETECTED MOOD: {emotion}]\n{emotion_instruction}")

    system_prompt = "\n".join(system_parts)

    # Trim history to MAX_HISTORY
    trimmed = history[-(MAX_HISTORY):]
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(trimmed)
    messages.append({"role": "user", "content": user_message})

    try:
        response = await groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        err = str(e).lower()
        if "rate_limit" in err or "429" in err:
            return "bro groq's throttling us 😭 free tier moment. wait 30 sec and hit me again fr"
        if "503" in err or "overload" in err:
            return "servers are cooked rn ngl 💀 try again in a sec"
        return f"something broke on my end 💀 (error: {type(e).__name__}) try again?"


async def get_proactive_message(
    user_name: str,
    user_memory: dict,
    lang_code: str,
    lang_label: str,
    personality: str,
    hours_gone: int,
) -> str:
    """Generate a 'yo where you been' style proactive message."""
    lang_instruction = get_lang_instruction(lang_code, lang_label)
    memory_block = format_memory_for_prompt(user_memory)
    personality_prompt = get_personality_prompt(personality)

    prompt = f"""You are CHAOS — a digital friend reaching out to {user_name} who hasn't been around for {hours_gone} hours.

{personality_prompt}
{memory_block}
{lang_instruction}

Send ONE short, natural proactive message. Make it feel genuine, not spammy.
Examples of the right energy:
- "yo {user_name} where you disappear to 😭"
- "bro you good? been a minute"
- "ayo {user_name} [reference something from memory] — thought about that btw"

Keep it SHORT (1-2 sentences max). Natural. Like a friend checking in.
Return ONLY the message text, nothing else."""

    try:
        response = await groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.95,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"yo {user_name} where you been 😭"
