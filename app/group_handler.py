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
    "debate":      0.25,   # arguments, opinions — bot loves these
    "question":    0.25,   # someone asked the group something
    "football":    0.20,   # football topics
    "gaming":      0.15,   # gaming topics
    "crypto":      0.15,   # crypto/money topics
    "shocking":    0.25,   # "omg", "no way", "what the"
    "funny":       0.15,   # lol, 😂, jokes
    "challenge":   0.20,   # "bet", "i dare", "prove it"
    "hot_take":    0.20,   # controversial opinions
    "default":     0.20,   # anything else — raised so it actually jumps in
}

# ── Rate limiting per group ───────────────────────────────────────────────────
# Prevents the bot from flooding a group
_group_last_reply: dict[int, float] = {}

# ── Message counter per group ─────────────────────────────────────────────────
# Guarantees bot jumps in at least every MAX_SILENCE messages
_group_msg_count: dict[int, int] = {}
_MAX_SILENCE = 30   # after this many messages with no jump-in, force one
_MIN_SECONDS_BETWEEN_REPLIES = 25  # spontaneous jump-ins: at most once per 25s per group

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
    # Always respond to direct triggers — these bypass rate limiter completely
    if is_mention:
        logger.info("[GROUP] replying because mention")
        return True, "mention"
    if is_reply:
        logger.info("[GROUP] replying because reply")
        return True, "reply"

    # Rate limit check — only applies to spontaneous jump-ins
    if _is_rate_limited(chat_id):
        _group_msg_count[chat_id] = _group_msg_count.get(chat_id, 0) + 1
        # Even if rate-limited, force jump-in after MAX_SILENCE messages
        if _group_msg_count.get(chat_id, 0) >= _MAX_SILENCE:
            _group_msg_count[chat_id] = 0
            return True, "jump_in"
        logger.info("[GROUP] skipped")
        return False, "skip"

    # Increment message counter
    _group_msg_count[chat_id] = _group_msg_count.get(chat_id, 0) + 1

    # Force jump-in if been silent too long
    if _group_msg_count[chat_id] >= _MAX_SILENCE:
        _group_msg_count[chat_id] = 0
        return True, "jump_in"

    # Detect topic and roll dice
    topic = _detect_topic(text)
    odds  = _JUMP_IN_ODDS.get(topic, _JUMP_IN_ODDS["default"])

    # Short messages — slight penalty but not huge
    if len(text.split()) < 2:
        odds *= 0.5

    if random.random() < odds:
        _group_msg_count[chat_id] = 0   # reset counter when jumping in
        logger.info("[GROUP] jumping into conversation")
        return True, "jump_in"

    logger.info("[GROUP] skipped")
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
