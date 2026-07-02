"""
stats.py — Bot analytics: in-memory counters + periodic DB flush.

Tracks:
  - Total unique users / groups
  - Messages today
  - AI requests today
  - Built-in replies used
  - Provider usage per provider
  - Average response time
  - Bot uptime

In-memory for speed (no DB write per message).
Flushes to DB every 10 minutes via APScheduler job.
/botstats — owner-only full analytics
/users    — owner-only user list summary
"""

import os
import time
import logging
import asyncio
from datetime import datetime, date
from collections import defaultdict

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))  # Set this in Railway vars

_start_time = time.time()

# In-memory counters (reset daily at midnight)
_counters: dict[str, int] = defaultdict(int)
_provider_usage: dict[str, int] = defaultdict(int)
_response_times: list[float] = []
_unique_users: set[int] = set()
_unique_groups: set[int] = set()
_last_reset_date: date = datetime.utcnow().date()

# Locks
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
        # Keep only last 100 for rolling average
        if len(_response_times) > 100:
            _response_times.pop(0)


async def record_builtin_reply():
    async with _lock:
        _maybe_reset_daily()
        _counters["builtin_replies_today"] += 1


async def record_sticker_reply():
    async with _lock:
        _counters["sticker_replies_today"] += 1


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


def get_stats_text() -> str:
    _maybe_reset_daily()
    provider_lines = "\n".join(
        f"  {name}: {count}" for name, count in sorted(_provider_usage.items(), key=lambda x: -x[1])
    ) or "  none yet"

    return (
        f"📊 Chaoz Analytics\n\n"
        f"🕐 Uptime: {get_uptime()}\n"
        f"👥 Unique users: {len(_unique_users)}\n"
        f"💬 Unique groups: {len(_unique_groups)}\n\n"
        f"📅 Today:\n"
        f"  Messages: {_counters['messages_today']}\n"
        f"  AI requests: {_counters['ai_requests_today']}\n"
        f"  Built-in replies: {_counters['builtin_replies_today']}\n"
        f"  Sticker replies: {_counters['sticker_replies_today']}\n\n"
        f"⚡ Avg response: {get_avg_response_time()}\n\n"
        f"🤖 Provider usage today:\n{provider_lines}"
    )


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_botstats(update, context):
    """Owner-only full analytics command."""
    if BOT_OWNER_ID and update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("owner only 🔒")
        return
    await update.message.reply_text(get_stats_text())


async def cmd_users(update, context):
    """Owner-only user summary."""
    if BOT_OWNER_ID and update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("owner only 🔒")
        return

    # Pull from DB for persistent counts
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import select, func
        from app.database import User

        async with AsyncSessionLocal() as db:
            total = await db.execute(select(func.count()).select_from(User))
            total_users = total.scalar_one() or 0

            # Count unique chat_ids from messages as group proxy
            from app.database import Message
            groups = await db.execute(
                select(func.count(func.distinct(Message.user_id))).select_from(Message)
            )
            active_users = groups.scalar_one() or 0

        await update.message.reply_text(
            f"👥 User Summary\n\n"
            f"Total registered users: {total_users}\n"
            f"Users with messages: {active_users}\n"
            f"Active this session: {len(_unique_users)}\n"
            f"Groups seen this session: {len(_unique_groups)}\n\n"
            f"Use /botstats for full analytics"
        )
    except Exception as e:
        await update.message.reply_text(f"couldn't fetch user data: {e}")
