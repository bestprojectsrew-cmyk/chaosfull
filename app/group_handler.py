"""
group_handler.py — Group chat logic for Chaos bot.

Behavior:
  - Always responds when mentioned (@botname) or directly replied to
  - Occasionally jumps in on interesting topics (configurable probability)
  - Mirrors the group's tone/energy automatically (no hardcoded personality)
  - Tracks recent group messages for context (last 10, in memory only)
  - Never responds to bots
  - Rate-limited per group to avoid spamming
"""

import re
import time
import random
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# ── Jump-in probability per topic type ───────────────────────────────────────
# These are the odds the bot spontaneously replies to an interesting message
_JUMP_IN_ODDS = {
    "debate":      0.60,   # arguments, opinions, "better", "worse", "goat"
    "question":    0.45,   # someone asked the group something
    "football":    0.55,   # football topics
    "gaming":      0.50,   # gaming topics
    "crypto":      0.50,   # crypto/money topics
    "shocking":    0.65,   # "omg", "no way", "what the"
    "funny":       0.40,   # lol, 😂, jokes
    "challenge":   0.55,   # "bet", "i dare", "prove it"
    "hot_take":    0.60,   # controversial opinions
    "default":     0.08,   # anything else — low baseline
}

# ── Rate limiting per group ───────────────────────────────────────────────────
# Prevents the bot from flooding a group
_group_last_reply: dict[int, float] = {}
_MIN_SECONDS_BETWEEN_REPLIES = 8   # don't reply more than once per 8 seconds per group

# ── Recent message buffer per group ──────────────────────────────────────────
# Stores last 10 messages per group for context (in memory, not DB)
_group_context: dict[int, deque] = defaultdict(lambda: deque(maxlen=10))

# ── Topic detection patterns ──────────────────────────────────────────────────
_TOPIC_PATTERNS = [
    ("debate",    re.compile(
        r"\b(better|worse|goat|best|worst|vs|versus|or|disagree|agree|opinion|think|believe|"
        r"lучше|хуже|мне кажется|думаю|считаю|yaxshi|yomon|menimcha)\b", re.I)),
    ("question",  re.compile(
        r"(\?|who|what|where|when|why|how|кто|что|где|когда|почему|как|kim|nima|qayer|qachon|nega|qanday)", re.I)),
    ("football",  re.compile(
        r"\b(goal|match|football|soccer|fifa|league|club|player|transfer|score|"
        r"гол|матч|футбол|клуб|игрок|трансфер|счёт|gol|o'yin|futbol)\b", re.I)),
    ("gaming",    re.compile(
        r"\b(game|gaming|play|player|rank|ranked|noob|pro|gg|clutch|win|lose|"
        r"игра|играть|игрок|ранг|победа|проиграл)\b", re.I)),
    ("crypto",    re.compile(
        r"\b(bitcoin|btc|eth|crypto|coin|token|pump|dump|price|buy|sell|"
        r"биткоин|крипта|монета|цена|купить|продать)\b", re.I)),
    ("shocking",  re.compile(
        r"\b(omg|no way|what the|bro|seriously|bruh|nah|"
        r"ого|серьёзно|что за|нет серьёзно|вот это|hay xudo|voy)\b", re.I)),
    ("funny",     re.compile(r"(😂|🤣|💀|lmao|lmfao|haha|хаха|lol)", re.I)),
    ("challenge", re.compile(r"\b(bet|dare|prove|challenge|i bet|"
        r"спорим|докажи|слабо)\b", re.I)),
    ("hot_take",  re.compile(
        r"\b(unpopular opinion|hot take|controversial|ngl|honestly|real talk|"
        r"честно говоря|по-честному|rost qilsam)\b", re.I)),
]


def _detect_topic(text: str) -> str:
    """Return the most interesting topic type found, or 'default'."""
    for topic, pattern in _TOPIC_PATTERNS:
        if pattern.search(text):
            return topic
    return "default"


def _is_rate_limited(chat_id: int) -> bool:
    """True if we replied to this group too recently."""
    last = _group_last_reply.get(chat_id, 0)
    return time.time() - last < _MIN_SECONDS_BETWEEN_REPLIES


def _mark_replied(chat_id: int) -> None:
    _group_last_reply[chat_id] = time.time()


def add_to_group_context(chat_id: int, username: str, text: str) -> None:
    """Store a message in the group's recent context buffer."""
    _group_context[chat_id].append(f"{username}: {text}")


def get_group_context(chat_id: int) -> str:
    """Return recent group messages as a formatted string for the LLM."""
    msgs = list(_group_context[chat_id])
    if not msgs:
        return ""
    return "[RECENT GROUP CHAT]\n" + "\n".join(msgs[-8:])


def should_jump_in(
    text: str,
    chat_id: int,
    is_mention: bool,
    is_reply: bool,
) -> tuple[bool, str]:
    """
    Decide whether the bot should respond to a group message.

    Returns (should_respond: bool, reason: str)
    Reason is one of: 'mention', 'reply', 'jump_in', 'skip'
    """
    # Always respond to direct triggers
    if is_mention:
        return True, "mention"
    if is_reply:
        return True, "reply"

    # Rate limit check — don't spam
    if _is_rate_limited(chat_id):
        return False, "skip"

    # Detect topic and roll dice
    topic = _detect_topic(text)
    odds  = _JUMP_IN_ODDS.get(topic, _JUMP_IN_ODDS["default"])

    # Short messages with no substance — lower the odds further
    if len(text.split()) < 3:
        odds *= 0.3

    if random.random() < odds:
        return True, "jump_in"

    return False, "skip"


def build_group_system_addition(
    group_context: str,
    group_name: str,
    reason: str,
) -> str:
    """
    Extra instructions added to the system prompt for group chat responses.
    """
    parts = []

    if group_context:
        parts.append(group_context)

    parts.append(
        f"\n[GROUP CHAT: {group_name}]\n"
        f"You are in a group chat. Multiple people are talking.\n"
        f"Mirror the group's tone EXACTLY — how they write, you write.\n"
        f"If they're being casual and chaotic, match that. If someone's being serious, match that.\n"
        f"Read the recent messages above and adapt your energy to fit in naturally.\n"
        f"Keep replies SHORT in groups — 1-3 sentences usually. Groups are fast-paced.\n"
        f"Don't address the whole group unless relevant. Reply to whoever triggered you."
    )

    if reason == "jump_in":
        parts.append(
            "\nYou're jumping into this conversation spontaneously — not because you were called.\n"
            "Make it feel natural, like a friend who just had something to say. Don't announce yourself."
        )

    return "\n".join(parts)
