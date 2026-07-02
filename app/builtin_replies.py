"""
builtin_replies.py

Very lightweight replies that do NOT use AI.

Only answers:
- thanks
- goodbye
- identity questions

Everything else returns None so the main group logic
can decide whether to ignore the message or call AI.
"""

import random
import re

# ──────────────────────────────────────────────────────────────
# Thanks
# ──────────────────────────────────────────────────────────────

_THANKS = re.compile(
    r"^(thanks?|thank you|thx|ty|rahmat|raxmat|спасибо|merci|gracias|teşekkür)[\s!.,🙏]*$",
    re.IGNORECASE,
)

_THANKS_REPLIES = [
    "np 🙌",
    "anytime bro",
    "no worries",
    "of course",
    "glad i could help",
]

# ──────────────────────────────────────────────────────────────
# Goodbye
# ──────────────────────────────────────────────────────────────

_FAREWELLS = re.compile(
    r"^(bye+|goodbye|cya|see ya|later|peace|xayr|пока|adios|gtg|ttyl)[\s!.,👋]*$",
    re.IGNORECASE,
)

_FAREWELL_REPLIES = [
    "later 👋",
    "take care",
    "peace ✌️",
    "see ya",
]

# ──────────────────────────────────────────────────────────────
# Identity
# ──────────────────────────────────────────────────────────────

BOT_OWNER = "@whozrew"

_IDENTITY = re.compile(
    r"^(who are you|who made you|who built you|who created you|"
    r"who is your owner|who is your creator|"
    r"what ai are you|what model are you|"
    r"tell me about yourself|powered by)\??$",
    re.IGNORECASE,
)

_IDENTITY_REPLIES = [
    f"I'm Chaoz 😎\nMade by {BOT_OWNER}.",
    f"Chaoz here 🤖\nBuilt by {BOT_OWNER}.",
    f"I'm Chaoz.\nCreated by {BOT_OWNER}.",
]

# ──────────────────────────────────────────────────────────────
# Name trigger
# ──────────────────────────────────────────────────────────────

_NAME_TRIGGER = re.compile(
    r"(^|\s)(chaoz)(\s|$|[!?.,])",
    re.IGNORECASE,
)

# ──────────────────────────────────────────────────────────────
# Public functions
# ──────────────────────────────────────────────────────────────

def get_builtin_reply(text: str) -> str | None:
    """
    Returns a lightweight reply or None.
    """

    text = text.strip()

    if not text:
        return None

    if _IDENTITY.match(text):
        return random.choice(_IDENTITY_REPLIES)

    if _THANKS.match(text):
        return random.choice(_THANKS_REPLIES)

    if _FAREWELLS.match(text):
        return random.choice(_FAREWELL_REPLIES)

    return None


def is_name_trigger(text: str) -> bool:
    """
    True if user explicitly says Chaoz.
    """

    return bool(_NAME_TRIGGER.search(text))
