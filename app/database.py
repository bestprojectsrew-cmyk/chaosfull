"""
database.py — PostgreSQL models v2: long-term memory, personality, emotions
"""
import os
from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, Integer, Text, String,
    DateTime, Boolean, JSON, Float, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_async_url(url: str) -> str:
    url = url.replace("postgres://", "postgresql+asyncpg://")
    url = url.replace("postgresql://", "postgresql+asyncpg://")
    return url


def _make_engine():
    url = get_async_url(DATABASE_URL)
    if not url or url.endswith("//"):
        return None
    return create_async_engine(
        url, echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10,
    )


async_engine = _make_engine()

AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False,
) if async_engine else None

Base = declarative_base()


class User(Base):
    """Core user record + active personality/language."""
    __tablename__ = "users"

    id            = Column(BigInteger, primary_key=True)   # Telegram user_id
    username      = Column(String(64),  nullable=True)
    first_name    = Column(String(64),  nullable=True)
    nickname      = Column(String(64),  nullable=True)     # what they want to be called
    language_code = Column(String(8),   nullable=True)     # last detected lang
    personality   = Column(String(32),  default="chaotic") # active /mode
    message_count = Column(Integer,     default=0)
    created_at    = Column(DateTime,    default=datetime.utcnow)
    last_seen     = Column(DateTime,    default=datetime.utcnow)
    last_proactive= Column(DateTime,    nullable=True)     # last "yo where you at" msg
    is_banned     = Column(Boolean,     default=False)


class UserMemory(Base):
    """
    Long-term structured memory per user.

    One row per user.

    Example JSON schema:

    {
        "nickname": "...",
        "birthday": "...",
        "fav_games": [...],
        "fav_football_club": "...",
        "fav_music": [...],
        "fav_movies": [...],
        "relationships": {
            "mom": "...",
            "bestie": "..."
        },
        "facts": [
            "User is from Tashkent",
            "User hates Mondays"
        ],
        "recent_topics": [...],
        "mood_history": [...]
    }
    """

    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=True, index=True)
    memory_scope = Column(String(20), nullable=False, default="global", index=True)
    data = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    """Full conversation log — all roles, all time."""
    __tablename__ = "messages"

    id         = Column(Integer,    primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, nullable=False)
    role       = Column(String(16), nullable=False)   # "user" | "assistant"
    content    = Column(Text,       nullable=False)
    language   = Column(String(8),  nullable=True)
    emotion    = Column(String(32), nullable=True)    # detected emotion
    created_at = Column(DateTime,   default=datetime.utcnow)



class GroupWarn(Base):
    """Tracks warnings per user per group. 3 warns = auto-ban."""
    __tablename__ = "group_warns"

    id         = Column(Integer,    primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, nullable=False)
    chat_id    = Column(BigInteger, nullable=False)
    warned_by  = Column(BigInteger, nullable=False)   # admin who warned
    reason     = Column(Text,       nullable=True)
    created_at = Column(DateTime,   default=datetime.utcnow)


class CoupleOfDay(Base):
    """Stores today's couple per group so it only generates once per day."""
    __tablename__ = "couple_of_day"

    id         = Column(Integer,    primary_key=True, autoincrement=True)
    chat_id    = Column(BigInteger, nullable=False)
    user1_id   = Column(BigInteger, nullable=False)
    user2_id   = Column(BigInteger, nullable=False)
    user1_name = Column(String(64), nullable=True)
    user2_name = Column(String(64), nullable=True)
    created_at = Column(DateTime,   default=datetime.utcnow)


class GroupFilter(Base):
    """Word/phrase filters per group with custom responses."""
    __tablename__ = "group_filters"

    id            = Column(Integer,     primary_key=True, autoincrement=True)
    chat_id       = Column(BigInteger,  nullable=False)
    trigger       = Column(String(256), nullable=False)
    response_text = Column(Text,        nullable=True)
    response_type = Column(String(16),  default="text")  # text / gif / photo / all
    is_regex      = Column(Boolean,     default=False)
    created_by    = Column(BigInteger,  nullable=True)
    created_at    = Column(DateTime,    default=datetime.utcnow)


class GroupNote(Base):
    """Saved notes per group — /savenote /getnote /delnote."""
    __tablename__ = "group_notes"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    chat_id    = Column(BigInteger,  nullable=False)
    name       = Column(String(128), nullable=False)
    content    = Column(Text,        nullable=False)
    created_by = Column(BigInteger,  nullable=True)
    created_at = Column(DateTime,    default=datetime.utcnow)


async def init_db():
    """Create all tables if they don't exist."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
