"""
memory.py — Long-term memory: fact extraction + prompt formatting.
Uses the cheap/fast model tier to minimize cost.
"""
import json
import re
import logging
from app import providers   # import lazily to avoid circular deps at module level

logger = logging.getLogger(__name__)

EMPTY_MEMORY: dict = {
    "nickname": None,
    "age": None,
    "city": None,
    "birthday": None,
    "job_or_school": None,
    "fav_games": [],
    "fav_football_club": None,
    "fav_music": [],
    "fav_movies": [],
    "fav_anime": [],
    "relationships": {},
    "facts": [],
    "recent_topics": [],
    "mood_history": [],
    "goals": [],
}


def format_memory_for_prompt(mem: dict) -> str:
    """Compact memory block injected into system prompt."""
    if not mem or not any(mem.values()):
        return ""

    parts = []
    if mem.get("nickname"):   parts.append(f"name: {mem['nickname']}")
    if mem.get("age"):        parts.append(f"age: {mem['age']}")
    if mem.get("city"):       parts.append(f"city: {mem['city']}")
    if mem.get("fav_football_club"): parts.append(f"club: {mem['fav_football_club']}")
    if mem.get("fav_games"):  parts.append(f"games: {', '.join(mem['fav_games'][:4])}")
    if mem.get("fav_music"):  parts.append(f"music: {', '.join(mem['fav_music'][:4])}")
    if mem.get("fav_movies"): parts.append(f"shows: {', '.join(mem['fav_movies'][:3])}")
    if mem.get("fav_anime"):  parts.append(f"anime: {', '.join(mem['fav_anime'][:3])}")
    if mem.get("job_or_school"): parts.append(f"work/school: {mem['job_or_school']}")
    if mem.get("relationships"):
        rel = ", ".join(f"{k}={v}" for k, v in list(mem["relationships"].items())[:4])
        parts.append(f"people: {rel}")
    if mem.get("facts"):
        parts.append(f"known: {'; '.join(mem['facts'][-6:])}")
    if mem.get("goals"):
        parts.append(f"goals: {', '.join(mem['goals'][:3])}")

    if not parts:
        return ""

    return "[MEMORY] " + " | ".join(parts)


async def extract_and_update_memory(
    user_message: str,
    current_memory: dict,
    scope: str = "global",
    chat_id: int | None = None,
) -> dict:
    """
    Extract new facts from user message and merge into existing memory.
    Routes extracted facts to the correct scope:
      global  — birthday, age, nickname, city, country, club, games, goals
      private — personal conversations, emotions, private plans
      group   — group-specific topics, jokes, interactions
    Uses cheap model. Returns updated dict unchanged if extraction fails.
    """
    # Scope-specific extraction instructions
    scope_instructions = {
        "global": (
            "Extract ONLY permanent personal facts: nickname, age, birthday, city, country, "
            "job_or_school, fav_football_club, fav_games, fav_music, fav_movies, fav_anime, "
            "relationships, goals. These are facts true everywhere about this person."
        ),
        "private": (
            "Extract ONLY private/personal conversation facts: emotional discussions, "
            "personal promises, private plans, private jokes, personal struggles. "
            "Do NOT extract general facts like age or city here."
        ),
        "group": (
            "Extract ONLY group-relevant facts: topics discussed in this group, "
            "group-specific jokes or references, how this person interacts in this group. "
            "Do NOT extract permanent personal facts like age or birthday here."
        ),
    }

    instruction = scope_instructions.get(scope, scope_instructions["global"])

    prompt = (
        f"Extract personal facts from this message and update the JSON. "
        f"{instruction} "
        f"Only add NEW info. Never delete existing. Return ONLY valid JSON.\n\n"
        f"CURRENT: {json.dumps(current_memory, ensure_ascii=False)}\n\n"
        f"MESSAGE: \"{user_message}\"\n\n"
        f"Fields: nickname, age, city, birthday, job_or_school, fav_games(list), "
        f"fav_football_club, fav_music(list), fav_movies(list), fav_anime(list), "
        f"relationships(dict), facts(list of short sentences), goals(list), "
        f"recent_topics(list). Return ONLY JSON, no markdown, no explanation."
    )
    try:
        raw = await providers.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,
            tier="memory",
        )
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        updated = json.loads(raw)
        for key in ("recent_topics", "mood_history", "facts"):
            if isinstance(updated.get(key), list):
                limits = {"recent_topics": 10, "mood_history": 5, "facts": 20}
                updated[key] = updated[key][-limits[key]:]
        return updated
    except Exception as e:
        logger.debug(f"Memory extraction failed (non-critical): {e}")
        return current_memory
