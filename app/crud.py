"""
crud.py — All DB operations: users, messages, long-term memory
"""
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.database import User, Message, UserMemory, BotGroup
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

async def get_user_memory(db: AsyncSession, user_id: int, chat_id: int = 0, is_group: bool = False) -> dict:
    """
    Load memory based on chat context.
    Private: global + private scopes.
    Group: global + group scope for this specific chat_id only.
    """
    from app.database import UserMemory
    from app.memory import EMPTY_MEMORY
    import copy

    # Always load global memory
    result = await db.execute(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.memory_scope == "global",
        )
    )
    global_mem = result.scalar_one_or_none()
    merged = copy.deepcopy(global_mem.data if global_mem else EMPTY_MEMORY)

    if is_group and chat_id:
        # Load this group's memory only — never another group's
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == user_id,
                UserMemory.chat_id == chat_id,
                UserMemory.memory_scope == "group",
            )
        )
        group_mem = result.scalar_one_or_none()
        if group_mem and group_mem.data:
            # Merge group facts on top of global
            group_data = group_mem.data
            for key, val in group_data.items():
                if isinstance(val, list) and isinstance(merged.get(key), list):
                    merged[key] = merged[key] + [v for v in val if v not in merged[key]]
                elif val:
                    merged[key] = val
    else:
        # Private chat: load private memory on top of global
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == user_id,
                UserMemory.memory_scope == "private",
            )
        )
        private_mem = result.scalar_one_or_none()
        if private_mem and private_mem.data:
            for key, val in private_mem.data.items():
                if isinstance(val, list) and isinstance(merged.get(key), list):
                    merged[key] = merged[key] + [v for v in val if v not in merged[key]]
                elif val:
                    merged[key] = val

    return merged


async def save_user_memory(
    db: AsyncSession,
    user_id: int,
    data: dict,
    scope: str = "global",
    chat_id: int | None = None,
) -> None:
    """
    Save memory to the correct scope.
    scope="global"  — permanent facts, visible everywhere
    scope="private" — private chat only, chat_id not needed
    scope="group"   — group specific, requires chat_id
    """
    from app.database import UserMemory

    # Build the filter conditions for upsert
    conditions = [
        UserMemory.user_id == user_id,
        UserMemory.memory_scope == scope,
    ]
    if scope == "group" and chat_id:
        conditions.append(UserMemory.chat_id == chat_id)

    result = await db.execute(select(UserMemory).where(*conditions))
    mem_row = result.scalar_one_or_none()

    if mem_row is None:
        mem_row = UserMemory(
            user_id=user_id,
            chat_id=chat_id if scope == "group" else None,
            memory_scope=scope,
            data=data,
            updated_at=datetime.utcnow(),
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


# ── Group filters ─────────────────────────────────────────────────────────────

async def add_filter(
    db: AsyncSession, chat_id: int, trigger: str,
    response_text: str | None, response_type: str,
    created_by: int, is_regex: bool = False,
) -> None:
    from app.database import GroupFilter
    await db.execute(
        delete(GroupFilter).where(
            GroupFilter.chat_id == chat_id,
            GroupFilter.trigger == trigger.lower(),
        )
    )
    f = GroupFilter(
        chat_id=chat_id, trigger=trigger.lower(),
        response_text=response_text, response_type=response_type,
        is_regex=is_regex, created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.add(f)
    await db.commit()


async def remove_filter(db: AsyncSession, chat_id: int, trigger: str) -> bool:
    from app.database import GroupFilter
    result = await db.execute(
        delete(GroupFilter).where(
            GroupFilter.chat_id == chat_id,
            GroupFilter.trigger == trigger.lower(),
        )
    )
    await db.commit()
    return result.rowcount > 0


async def get_filters(db: AsyncSession, chat_id: int) -> list:
    from app.database import GroupFilter
    result = await db.execute(
        select(GroupFilter).where(GroupFilter.chat_id == chat_id)
    )
    return result.scalars().all()


async def get_matching_filter(db: AsyncSession, chat_id: int, text: str):
    import re as _re
    from app.database import GroupFilter
    result = await db.execute(
        select(GroupFilter).where(GroupFilter.chat_id == chat_id)
    )
    filters = result.scalars().all()
    text_lower = text.lower()
    for f in filters:
        try:
            if f.is_regex:
                if _re.search(f.trigger, text_lower, _re.IGNORECASE):
                    return f
            else:
                if f.trigger in text_lower:
                    return f
        except Exception:
            pass
    return None


# ── Group notes ───────────────────────────────────────────────────────────────

async def save_note(
    db: AsyncSession, chat_id: int, name: str, content: str, created_by: int
) -> None:
    from app.database import GroupNote
    await db.execute(
        delete(GroupNote).where(
            GroupNote.chat_id == chat_id,
            GroupNote.name == name.lower(),
        )
    )
    note = GroupNote(
        chat_id=chat_id, name=name.lower(),
        content=content, created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.add(note)
    await db.commit()


async def get_note(db: AsyncSession, chat_id: int, name: str):
    from app.database import GroupNote
    result = await db.execute(
        select(GroupNote).where(
            GroupNote.chat_id == chat_id,
            GroupNote.name == name.lower(),
        )
    )
    return result.scalar_one_or_none()


async def delete_note(db: AsyncSession, chat_id: int, name: str) -> bool:
    from app.database import GroupNote
    result = await db.execute(
        delete(GroupNote).where(
            GroupNote.chat_id == chat_id,
            GroupNote.name == name.lower(),
        )
    )
    await db.commit()
    return result.rowcount > 0


async def list_notes(db: AsyncSession, chat_id: int) -> list:
    from app.database import GroupNote
    result = await db.execute(
        select(GroupNote).where(GroupNote.chat_id == chat_id)
    )
    return result.scalars().all()

async def save_group(
    db: AsyncSession,
    chat_id: int,
    title: str,
    username: str | None,
    chat_type: str,
) -> bool:
    """Create or update a group record.
    Returns True if this is a brand-new group.
    """

    result = await db.execute(
        select(BotGroup).where(BotGroup.chat_id == chat_id)
    )
    group = result.scalar_one_or_none()

    if group is None:
        group = BotGroup(
            chat_id=chat_id,
            title=title,
            username=username,
            chat_type=chat_type,
            joined_at=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        db.add(group)
        await db.commit()
        return True

    group.title = title
    group.username = username
    group.chat_type = chat_type
    group.last_seen = datetime.utcnow()

    await db.commit()
    return False

async def get_all_groups(db: AsyncSession):
    """Return all groups ordered by latest activity."""
    result = await db.execute(
        select(BotGroup).order_by(BotGroup.last_seen.desc())
    )
    return result.scalars().all()

async def get_all_users(db: AsyncSession):
    """Return all registered users."""
    result = await db.execute(select(User))
    return result.scalars().all()

# ── Chaoz Memories ───────────────────────────────────────────────────────────

async def save_chaoz_memory(
    db: AsyncSession,
    memory_type: str,
    story: str,
    importance: int = 1,
):
    from app.database import ChaozMemory

    memory = ChaozMemory(
        memory_type=memory_type,
        story=story,
        importance=importance,
        created_at=datetime.utcnow(),
    )

    db.add(memory)
    await db.commit()


async def get_random_chaoz_memory(db: AsyncSession):
    from app.database import ChaozMemory
    from sqlalchemy import func

    result = await db.execute(
        select(ChaozMemory)
        .order_by(func.random())
        .limit(1)
    )

    return result.scalar_one_or_none()


async def get_recent_chaoz_memories(
    db: AsyncSession,
    limit: int = 10,
):
    from app.database import ChaozMemory

    result = await db.execute(
        select(ChaozMemory)
        .order_by(ChaozMemory.created_at.desc())
        .limit(limit)
    )

    return result.scalars().all()


async def cleanup_chaoz_memories(
    db: AsyncSession,
    keep: int = 500,
):
    from app.database import ChaozMemory

    result = await db.execute(
        select(ChaozMemory.id)
        .order_by(ChaozMemory.created_at.desc())
    )

    ids = [x[0] for x in result.all()]

    if len(ids) <= keep:
        return

    remove_ids = ids[keep:]

    await db.execute(
        delete(ChaozMemory).where(
            ChaozMemory.id.in_(remove_ids)
        )
    )

    await db.commit()
