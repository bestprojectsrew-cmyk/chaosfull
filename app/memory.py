"""
memory.py — Long-term user memory: extract facts from conversation and recall them
"""
import json
import re
from datetime import datetime
from groq import AsyncGroq
import os

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", ""))
MODEL = "llama-3.1-70b-versatile"

EMPTY_MEMORY = {
    "nickname": None,
    "birthday": None,
    "fav_games": [],
    "fav_football_club": None,
    "fav_music": [],
    "fav_movies": [],
    "fav_anime": [],
    "relationships": {},      # {"mom": "name", "bestie": "name"}
    "facts": [],              # free-form facts: ["lives in Tashkent", "hates Mondays"]
    "recent_topics": [],      # last 10 topics
    "mood_history": [],       # last 5 moods
    "goals": [],              # things they want to do/achieve
    "age": None,
    "city": None,
    "job_or_school": None,
}


def format_memory_for_prompt(mem: dict) -> str:
    """Turn the memory dict into a natural-language context block for the LLM."""
    if not mem:
        return "No long-term memory yet for this user."

    lines = ["[WHAT YOU REMEMBER ABOUT THIS PERSON]"]

    if mem.get("nickname"):
        lines.append(f"• They go by: {mem['nickname']}")
    if mem.get("age"):
        lines.append(f"• Age: {mem['age']}")
    if mem.get("city"):
        lines.append(f"• Lives in: {mem['city']}")
    if mem.get("birthday"):
        lines.append(f"• Birthday: {mem['birthday']}")
    if mem.get("job_or_school"):
        lines.append(f"• Job/school: {mem['job_or_school']}")
    if mem.get("fav_football_club"):
        lines.append(f"• Football club: {mem['fav_football_club']}")
    if mem.get("fav_games"):
        lines.append(f"• Games they play: {', '.join(mem['fav_games'][:5])}")
    if mem.get("fav_music"):
        lines.append(f"• Music they like: {', '.join(mem['fav_music'][:5])}")
    if mem.get("fav_movies"):
        lines.append(f"• Movies/shows: {', '.join(mem['fav_movies'][:5])}")
    if mem.get("fav_anime"):
        lines.append(f"• Anime: {', '.join(mem['fav_anime'][:5])}")
    if mem.get("relationships"):
        rel_strs = [f"{k}: {v}" for k, v in list(mem["relationships"].items())[:5]]
        lines.append(f"• People in their life: {', '.join(rel_strs)}")
    if mem.get("goals"):
        lines.append(f"• Their goals: {', '.join(mem['goals'][:3])}")
    if mem.get("facts"):
        lines.append(f"• Things you know: {'; '.join(mem['facts'][-8:])}")
    if mem.get("recent_topics"):
        lines.append(f"• Recently talked about: {', '.join(mem['recent_topics'][-5:])}")
    if mem.get("mood_history"):
        lines.append(f"• Recent mood trend: {', '.join(mem['mood_history'][-3:])}")

    lines.append(
        "\nUSE THIS NATURALLY. Reference it like a real friend would — "
        "not like reading a file. Say 'bro you mentioned...' or 'wait weren't you into...' "
        "when it's relevant. Don't dump all of it at once."
    )
    return "\n".join(lines)


async def extract_and_update_memory(
    user_message: str,
    current_memory: dict,
) -> dict:
    """
    Ask the LLM to extract any new facts from the user's message
    and merge into the existing memory. Returns updated memory dict.
    Only runs occasionally (every ~5 messages) to save API calls.
    """
    current_json = json.dumps(current_memory, ensure_ascii=False)

    prompt = f"""You are a memory extractor. Extract personal facts from this user message and update the memory JSON.

CURRENT MEMORY:
{current_json}

USER SAID:
"{user_message}"

Update the memory JSON with any NEW facts you can extract. Only add things that are actually stated or clearly implied.
Fields to update if found: nickname, birthday, fav_games, fav_football_club, fav_music, fav_movies, fav_anime, relationships, facts, goals, age, city, job_or_school.

For "facts" array: add short factual sentences like "Doesn't like mornings", "Has a dog named Max".
For "recent_topics": add what this message is about (1-3 words).
Keep existing data. Only ADD or UPDATE, never delete existing facts.
Return ONLY valid JSON, nothing else, no markdown, no explanation."""

    try:
        response = await groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.1,  # Low temp for extraction accuracy
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()
        updated = json.loads(raw)
        # Ensure recent_topics doesn't grow forever
        if "recent_topics" in updated:
            updated["recent_topics"] = updated["recent_topics"][-10:]
        if "mood_history" in updated:
            updated["mood_history"] = updated["mood_history"][-5:]
        return updated
    except Exception:
        # If extraction fails, return current memory unchanged
        return current_memory
