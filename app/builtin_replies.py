import os
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
    "wassup",
    "ayooo",
    "yooo 😭",
    "heyyyy",
    "ayo what's poppin",
    "yo 🫡",
    "yurrr",
    "hey what's up",
    "sup sup",
    "hi hi",
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
    "always",
    "that's what i'm here for",
    "easy 🤝",
    "bet",
    "🙏",
    "real ones help fr",
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

BOT_OWNER = os.getenv("BOT_OWNER_USERNAME", "@whozrew")  # Set BOT_OWNER_USERNAME in Railway vars

_IDENTITY_REPLIES = [
    f"I'm Chaoz 😎\nMade by {BOT_OWNER}.\nPowered by multiple AI providers working together.",
    f"Chaoz here 🤖\nBuilt by {BOT_OWNER}, running on a mix of AI models under the hood.",
    f"that's me — Chaoz 😭\n{BOT_OWNER} built me. i run on several AI providers at once so i never go down.",
    f"name's Chaoz ✌️\n{BOT_OWNER} put me together. multiple AI providers keeping me alive 24/7.",
    f"Chaoz 🔥\ncreated by {BOT_OWNER}. i'm not one model — i use several providers so i stay up even when one dies.",
    f"it's Chaoz fr\n{BOT_OWNER} made me. powered by a bunch of AI models working together in the background.",
    f"yeah that's me, Chaoz 😭\nmy creator is {BOT_OWNER}. ask me anything fr",
]

# ── Name-trigger detection (group mentions without @) ─────────────────────────
_NAME_TRIGGERS = re.compile(
    r"\b(chaoz?|chaos)\b",
    re.IGNORECASE,
)


def get_builtin_reply(text: str) -> str | None:
    """
    Smart builtin replies.

    Only answer very simple social messages.
    Everything else goes to the AI.
    """

    stripped = text.strip()

    if not stripped:
        return None

    lower = stripped.lower()
    words = stripped.split()

    # Real conversations should ALWAYS go to AI
    if (
        len(words) >= 4
        or "?" in stripped
        or lower.startswith((
            "what", "why", "how", "when", "where", "who",
            "can ", "could ", "would ", "should ",
            "please", "tell", "explain"
        ))
        or lower.startswith((
            "nima", "nega", "qanday", "qachon", "kim",
            "iltimos", "tushuntir"
        ))
        or lower.startswith((
            "что", "почему", "как", "когда", "кто",
            "объясни", "скажи"
        ))
    ):
        return None

    # Identity questions
    if _IDENTITY.search(stripped):
        return random.choice(_IDENTITY_REPLIES)

    # Greetings
    if _GREETINGS.match(stripped):
        return random.choice([
            "hey 👋",
            "hello 😄",
            "yo bro",
            "what's good",
            "heyy",
            "sup 😎",
            "hey, what's up?",
            "yo 👀",
            "good to see you 😄",
            "wassup bro",
        ])

    # Thanks
    if _THANKS.match(stripped):
        return random.choice([
            "you're welcome 😄",
            "anytime bro 🤝",
            "no worries",
            "glad I could help",
            "of course",
            "always bro",
            "my pleasure",
        ])

    # Farewell
    if _FAREWELLS.match(stripped):
        return random.choice([
            "take care 👋",
            "later bro 😎",
            "bye 👋",
            "see ya",
            "have a good one",
        ])

    # Emoji only
    if _EMOJI_PATTERN.match(stripped):
        if random.random() < 0.30:
            return random.choice([
                "😂",
                "😭😂",
                "💀",
                "LMAOO 😭",
                "bro 💀",
                "😭",
            ])
        return None

    # Filler words
    if _FILLERS.match(stripped):
        # Only answer around 15% of the time
        if random.random() < 0.15:
            return random.choice([
                "real 😂",
                "fr",
                "facts",
                "same",
                "ong",
                "😂",
                "true tho",
            ])
        return None

    return None


def is_name_trigger(text: str) -> bool:
    """
    Returns True if the message contains 'chaoz', 'chaos', etc.
    Used in groups to detect when someone is talking TO the bot
    without using @mention.
    """
    return bool(_NAME_TRIGGERS.search(text))
