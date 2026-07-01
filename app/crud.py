"""
crud.py — All DB operations: users, messages, long-term memory
"""
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.database import User, Message, UserMemory
from app.memory import EMPTY_MEMORY


# ── User ─────────────────────────────────────────────────────────────────────

async def get_or_create_user(
    db: AsyncSession,
    user_id: int,
    username: str | None,
    first_name: str | None,
    lang_code: str | None,
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            id=user_id, username=username, first_name=first_name,
            language_code=lang_code, message_count=1,
            created_at=datetime.utcnow(), last_seen=datetime.utcnow(),
        )
        db.add(user)
    else:
        user.username = username
        user.first_name = first_name
        user.message_count = (user.message_count or 0) + 1
        user.last_seen = datetime.utcnow()
        if lang_code:
            user.language_code = lang_code
    await db.commit()
    await db.refresh(user)
    return user


async def is_banned(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User.is_banned).where(User.id == user_id))
    val = result.scalar_one_or_none()
    return bool(val)


async def update_user_language(db: AsyncSession, user_id: int, lang_code: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.language_code = lang_code
        await db.commit()


async def get_user_personality(db: AsyncSession, user_id: int) -> str:
    result = await db.execute(select(User.personality).where(User.id == user_id))
    val = result.scalar_one_or_none()
    return val or "chaotic"


async def set_user_personality(db: AsyncSession, user_id: int, mode: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.personality = mode
        await db.commit()


async def update_last_proactive(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.last_proactive = datetime.utcnow()
        await db.commit()


async def get_inactive_users(db: AsyncSession, hours: int = 48) -> list[User]:
    """Get users who haven't been seen in `hours` hours for proactive messages."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(User).where(
            User.last_seen < cutoff,
            User.is_banned == False,
            User.message_count > 3,   # Only users who've actually chatted
        )
    )
    return result.scalars().all()


# ── Messages ──────────────────────────────────────────────────────────────────

async def save_message(
    db: AsyncSession, user_id: int, role: str, content: str,
    language: str | None = None, emotion: str | None = None,
) -> None:
    msg = Message(
        user_id=user_id, role=role, content=content,
        language=language, emotion=emotion, created_at=datetime.utcnow(),
    )
    db.add(msg)
    await db.commit()


async def get_recent_history(
    db: AsyncSession, user_id: int, limit: int = 20,
) -> list[dict]:
    """Last N messages as LLM-ready dicts, chronological order."""
    result = await db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]


async def clear_history(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(delete(Message).where(Message.user_id == user_id))
    await db.commit()
    return result.rowcount


async def get_message_count(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count()).where(Message.user_id == user_id)
    )
    return result.scalar_one() or 0


# ── Long-term Memory ──────────────────────────────────────────────────────────

async def get_user_memory(db: AsyncSession, user_id: int) -> dict:
    """Returns the user's memory dict. Creates empty record if none exists."""
    result = await db.execute(
        select(UserMemory).where(UserMemory.user_id == user_id)
    )
    mem_row = result.scalar_one_or_none()
    if mem_row is None:
        return dict(EMPTY_MEMORY)
    return mem_row.data or dict(EMPTY_MEMORY)


async def save_user_memory(db: AsyncSession, user_id: int, data: dict) -> None:
    """Upsert the user's memory blob."""
    result = await db.execute(
        select(UserMemory).where(UserMemory.user_id == user_id)
    )
    mem_row = result.scalar_one_or_none()
    if mem_row is None:
        mem_row = UserMemory(
            user_id=user_id, data=data, updated_at=datetime.utcnow()
        )
        db.add(mem_row)
    else:
        mem_row.data = data
        mem_row.updated_at = datetime.utcnow()
    await db.commit()


async def update_mood_in_memory(
    db: AsyncSession, user_id: int, emotion: str
) -> None:
    """Append detected emotion to mood_history in memory."""
    if emotion == "neutral":
        return
    mem = await get_user_memory(db, user_id)
    history = mem.get("mood_history", [])
    history.append(emotion)
    mem["mood_history"] = history[-5:]
    await save_user_memory(db, user_id, mem)


# ── Group warns ───────────────────────────────────────────────────────────────

async def add_warn(
    db: AsyncSession, user_id: int, chat_id: int, warned_by: int, reason: str | None
) -> int:
    """Add a warning. Returns total warn count for this user in this group."""
    from app.database import GroupWarn
    warn = GroupWarn(
        user_id=user_id, chat_id=chat_id,
        warned_by=warned_by, reason=reason,
        created_at=datetime.utcnow(),
    )
    db.add(warn)
    await db.commit()
    result = await db.execute(
        select(func.count()).where(
            GroupWarn.user_id == user_id,
            GroupWarn.chat_id == chat_id,
        )
    )
    return result.scalar_one() or 0


async def get_warn_count(db: AsyncSession, user_id: int, chat_id: int) -> int:
    from app.database import GroupWarn
    result = await db.execute(
        select(func.count()).where(
            GroupWarn.user_id == user_id,
            GroupWarn.chat_id == chat_id,
        )
    )
    return result.scalar_one() or 0


async def reset_warns(db: AsyncSession, user_id: int, chat_id: int) -> None:
    from app.database import GroupWarn
    await db.execute(
        delete(GroupWarn).where(
            GroupWarn.user_id == user_id,
            GroupWarn.chat_id == chat_id,
        )
    )
    await db.commit()


# ── Couple of the day ─────────────────────────────────────────────────────────

async def get_couple_of_day(db: AsyncSession, chat_id: int):
    """Returns today's couple row for this group, or None if not generated yet."""
    from app.database import CoupleOfDay
    today = datetime.utcnow().date()
    result = await db.execute(
        select(CoupleOfDay).where(
            CoupleOfDay.chat_id == chat_id,
            func.date(CoupleOfDay.created_at) == today,
        )
    )
    return result.scalar_one_or_none()


async def save_couple_of_day(
    db: AsyncSession, chat_id: int,
    user1_id: int, user2_id: int,
    user1_name: str, user2_name: str,
):
    from app.database import CoupleOfDay
    couple = CoupleOfDay(
        chat_id=chat_id,
        user1_id=user1_id, user2_id=user2_id,
        user1_name=user1_name, user2_name=user2_name,
        created_at=datetime.utcnow(),
    )
    db.add(couple)
    await db.commit()
    return couple
