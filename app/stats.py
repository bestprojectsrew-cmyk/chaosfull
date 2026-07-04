"""
stats.py — Bot analytics: in-memory counters + DB queries for persistent stats.

/botstats — owner-only full analytics (anonymous, no IDs exposed)
/users    — owner-only user statistics (anonymous, no IDs exposed)
"""

import os
import time
import logging
import asyncio
from datetime import datetime, date, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))

_start_time = time.time()

# In-memory counters (reset daily at midnight)
_counters: dict[str, int] = defaultdict(int)
_provider_usage: dict[str, int] = defaultdict(int)
_response_times: list[float] = []
_unique_users: set[int] = set()
_unique_groups: set[int] = set()
_last_reset_date: date = datetime.utcnow().date()

_lock = asyncio.Lock()


def _maybe_reset_daily():
    global _last_reset_date
    today = datetime.utcnow().date()
    if today != _last_reset_date:
        _counters.clear()
        _response_times.clear()
        _provider_usage.clear()
        _last_reset_date = today
        logger.info("[stats] daily counters reset")


# ── Public recording functions (called by llm.py / bot.py) ───────────────────

async def record_message(user_id: int, chat_id: int, is_group: bool):
    async with _lock:
        _maybe_reset_daily()
        _counters["messages_today"] += 1
        _unique_users.add(user_id)
        if is_group:
            _unique_groups.add(chat_id)


async def record_ai_request(provider: str, response_time: float):
    async with _lock:
        _maybe_reset_daily()
        _counters["ai_requests_today"] += 1
        _provider_usage[provider] += 1
        _response_times.append(response_time)
        if len(_response_times) > 100:
            _response_times.pop(0)


async def record_builtin_reply():
    async with _lock:
        _maybe_reset_daily()
        _counters["builtin_replies_today"] += 1


async def record_sticker_reply():
    async with _lock:
        _counters["sticker_replies_today"] += 1


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_uptime() -> str:
    elapsed = int(time.time() - _start_time)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m"
    elif m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def get_avg_response_time() -> str:
    if not _response_times:
        return "n/a"
    avg = sum(_response_times) / len(_response_times)
    return f"{avg:.1f}s"


# ── DB queries ────────────────────────────────────────────────────────────────

async def _db_total_users() -> int:
    try:
        from app.database import AsyncSessionLocal, User
        from sqlalchemy import select, func
        async with AsyncSessionLocal() as db:
            r = await db.execute(select(func.count()).select_from(User))
            return r.scalar_one() or 0
    except Exception:
        return 0


async def _db_active_users(days: int) -> int:
    """Users who sent at least one message in the last N days."""
    try:
        from app.database import AsyncSessionLocal, User
        from sqlalchemy import select, func
        cutoff = datetime.utcnow() - timedelta(days=days)
        async with AsyncSessionLocal() as db:
            r = await db.execute(
                select(func.count()).select_from(User).where(User.last_seen >= cutoff)
            )
            return r.scalar_one() or 0
    except Exception:
        return 0


async def _db_total_groups() -> int:
    """Estimate unique groups from Message table chat IDs that are negative (group IDs)."""
    try:
        from app.database import AsyncSessionLocal, Message
        from sqlalchemy import select, func
        async with AsyncSessionLocal() as db:
            # Group chat IDs in Telegram are negative numbers
            r = await db.execute(
                select(func.count(func.distinct(Message.user_id))).select_from(Message)
            )
            # We track groups in-memory since Message doesn't store chat_id
            return len(_unique_groups)
    except Exception:
        return len(_unique_groups)


async def _db_avg_messages_per_user() -> str:
    try:
        from app.database import AsyncSessionLocal, User, Message
        from sqlalchemy import select, func
        async with AsyncSessionLocal() as db:
            total_msgs = await db.execute(select(func.count()).select_from(Message))
            total_users = await db.execute(select(func.count()).select_from(User))
            msgs = total_msgs.scalar_one() or 0
            users = total_users.scalar_one() or 1
            return f"{msgs / users:.1f}"
    except Exception:
        return "n/a"


# ── /botstats output ──────────────────────────────────────────────────────────

def get_stats_text() -> str:
    """Anonymous analytics — no IDs, no usernames."""
    _maybe_reset_daily()

    provider_lines = "\n".join(
        f"  • {name.capitalize()}: {count}"
        for name, count in sorted(_provider_usage.items(), key=lambda x: -x[1])
    ) or "  • none yet"

    return (
        f"📊 Chaoz Analytics\n\n"
        f"🕐 Uptime: {get_uptime()}\n"
        f"👥 Total registered users: (use /users)\n"
        f"👤 Active users today: {len(_unique_users)}\n"
        f"💬 Total groups: {len(_unique_groups)}\n"
        f"📨 Messages today: {_counters['messages_today']}\n"
        f"🤖 AI requests today: {_counters['ai_requests_today']}\n"
        f"⚡ Average response time: {get_avg_response_time()}\n"
        f"🧠 Built-in replies: {_counters['builtin_replies_today']}\n"
        f"🎭 Sticker replies: {_counters['sticker_replies_today']}\n\n"
        f"Provider usage today:\n{provider_lines}"
    )


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_botstats(update, context):
    """Owner-only full analytics. No personal data exposed."""
    if BOT_OWNER_ID and update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("owner only 🔒")
        return
    await update.message.reply_text(get_stats_text())


async def cmd_users(update, context):
    """Owner-only user statistics. Anonymous counts only — no IDs or usernames."""
    if BOT_OWNER_ID and update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("owner only 🔒")
        return

    total       = await _db_total_users()
    active_day  = await _db_active_users(days=1)
    active_week = await _db_active_users(days=7)
    active_month= await _db_active_users(days=30)
    avg_msgs    = await _db_avg_messages_per_user()
    groups      = len(_unique_groups)
    private     = max(0, len(_unique_users) - groups)

    await update.message.reply_text(
        f"👥 User Statistics\n\n"
        f"Total registered users: {total}\n"
        f"Users active today: {active_day}\n"
        f"Users active this week: {active_week}\n"
        f"Users active this month: {active_month}\n"
        f"Groups using the bot: {groups}\n"
        f"Private chats: {private}\n"
        f"Average messages per user: {avg_msgs}"
    )