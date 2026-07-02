"""
builtin_replies.py — Instant replies that never touch an AI provider.

Used for:
- Greetings (hi, hello, salom, etc.)
- Thanks / farewells
- Emoji-only messages
- Very short filler messages (ok, lol, bro)
- Bot identity questions (who made you, what model, etc.)

This cuts provider usage significantly for high-traffic groups
where many messages are just social filler.
"""

import re
import random

# ── Greeting patterns ─────────────────────────────────────────────────────────
_GREETINGS = re.compile(
    r"^(hi+|hey+|hello+|yo+|sup|salom|привет|salut|hola|ciao|merhaba|"
    r"assalomu alaykum|salam|ассалому алейкум|ку|здарова|даров|"
    r"good morning|good evening|good night|gm|gn|gn bro)"
    r"[\s!?.,🙂😊👋]*$",
    re.IGNORECASE,
)

_GREETING_REPLIES = [
    "hey 👋",
    "yo what's good",
    "heyy",
    "sup",
    "ayo",
    "heyyy what's up",
    "yo 👀",
    "what's good 🔥",
    "hii",
    "hey hey",
]

# ── Thanks patterns ───────────────────────────────────────────────────────────
_THANKS = re.compile(
    r"^(thanks?|thank you|thx|ty|rahmat|спасибо|merci|gracias|teşekkür|"
    r"raxmat|tashakkur|danke|arigatou|감사)[\s!.,🙏]*$",
    re.IGNORECASE,
)

_THANKS_REPLIES = [
    "np 🙌",
    "anytime",
    "of course",
    "no worries",
    "👍",
    "sure thing",
    "glad i could help",
]

# ── Farewell patterns ─────────────────────────────────────────────────────────
_FAREWELLS = re.compile(
    r"^(bye+|goodbye|cya|see ya|later|peace|xayr|пока|au revoir|adios|"
    r"tschüss|sayonara|gotta go|gtg|ttyl)[\s!.,👋]*$",
    re.IGNORECASE,
)

_FAREWELL_REPLIES = [
    "later 👋",
    "bye ✌️",
    "see ya",
    "take care",
    "peace out",
    "catch you later",
]

# ── Filler messages ───────────────────────────────────────────────────────────
_FILLERS = re.compile(
    r"^(ok|okay|ok+|k|kk|lol|lmao|haha|😂|💀|🤣|bro|bruh|fr|ngl|"
    r"same|true|facts|word|bet|aight|ight|yes|no|yep|nope|yup|nah|"
    r"nice|cool|wow|damn|omg|wtf|oof|rip|gg|nvm|idk)[\s!?.,]*$",
    re.IGNORECASE,
)

_FILLER_REPLIES = [
    "😭",
    "💀",
    "fr tho",
    "real",
    "lmao",
    "bro 💀",
    "ong",
    "exactly",
    "same ngl",
    "😂",
    "lowkey",
    "yeah bro",
]

# ── Emoji-only detection ──────────────────────────────────────────────────────
_EMOJI_PATTERN = re.compile(
    r"^[\U00010000-\U0010ffff\u2600-\u27BF\u2B00-\u2BFF\u1F000-\u1FFFF\s]+$"
)

_EMOJI_REPLIES = [
    "😭",
    "💀",
    "🔥",
    "fr",
    "same energy",
    "👀",
    "bro 😭",
    "lmaooo",
]

# ── Identity questions ────────────────────────────────────────────────────────
_IDENTITY = re.compile(
    r"\b(who made you|who built you|who created you|who is your (owner|creator|developer)|"
    r"what (model|ai|llm) are you|are you (gpt|chatgpt|gemini|claude|llama)|"
    r"what are you|tell me about yourself|your (owner|creator|dev)|"
    r"kim yasadi|kim yaratdi|кто тебя создал|кто твой создатель|"
    r"powered by|what powers you|your source)\b",
    re.IGNORECASE,
)

BOT_OWNER = "@whozrew"  # Update this to your actual username

_IDENTITY_REPLIES = [
    f"I'm Chaoz 😎\nMade by {BOT_OWNER}.\nPowered by multiple AI providers working together.",
    f"Chaoz here 🤖\nBuilt by {BOT_OWNER}, running on a mix of AI models under the hood.",
    f"that's me — Chaoz 😭\n{BOT_OWNER} built me. i run on several AI providers at once so i never go down.",
]

# ── Name-trigger detection (group mentions without @) ─────────────────────────
_NAME_TRIGGERS = re.compile(
    r"\b(chaoz?|chaos)\b",
    re.IGNORECASE,
)


def get_builtin_reply(text: str) -> str | None:
    """
    Check if message can be answered without AI.
    Returns a reply string or None (meaning: use AI).
    """
    stripped = text.strip()

    # Empty
    if not stripped:
        return "..."

    # Identity questions — check FIRST before any filler detection
    if _IDENTITY.search(stripped):
        return random.choice(_IDENTITY_REPLIES)

    # Emoji only
    if _EMOJI_PATTERN.match(stripped) and len(stripped) < 20:
        return random.choice(_EMOJI_REPLIES)

    # Greetings
    if _GREETINGS.match(stripped):
        return random.choice(_GREETING_REPLIES)

    # Thanks
    if _THANKS.match(stripped):
        return random.choice(_THANKS_REPLIES)

    # Farewells
    if _FAREWELLS.match(stripped):
        return random.choice(_FAREWELL_REPLIES)

    # Filler
    if _FILLERS.match(stripped):
        return random.choice(_FILLER_REPLIES)

    return None


def is_name_trigger(text: str) -> bool:
    """
    Returns True if the message contains 'chaoz', 'chaos', etc.
    Used in groups to detect when someone is talking TO the bot
    without using @mention.
    """
    return bool(_NAME_TRIGGERS.search(text))
