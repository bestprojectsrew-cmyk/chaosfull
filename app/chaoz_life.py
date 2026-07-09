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
