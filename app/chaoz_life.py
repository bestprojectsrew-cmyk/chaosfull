from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import save_chaoz_memory, cleanup_chaoz_memories


async def record_chaoz_memory(
    db: AsyncSession,
    story: str,
    memory_type: str = "general",
    importance: int = 1,
):
    """
    The ONLY function that should save Chaoz memories.

    Every future feature (roasts, milestones, games, moderation,
    funny moments...) should call this instead of writing directly
    to the database.
    """

    story = story.strip()

    if not story:
        return

    if len(story) > 250:
        story = story[:250]

    await save_chaoz_memory(
        db=db,
        memory_type=memory_type,
        story=story,
        importance=importance,
    )

    await cleanup_chaoz_memories(db)

from app.crud import get_recent_chaoz_memories


async def build_daily_story(db):
    """
    Build one short story from Chaoz's recent memories.
    """

    memories = await get_recent_chaoz_memories(db, limit=5)

    if not memories:
        return None

    lines = [m.story for m in memories]

    return (
        "Recent things I remember:\n"
        + "\n".join(f"• {x}" for x in lines)
    )