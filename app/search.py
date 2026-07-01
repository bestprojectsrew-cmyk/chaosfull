"""
search.py — Live web search with a real intent classifier (not keyword roulette).

Primary: Tavily — built for AI agents, 1000 free credits/month, stable.
Backup:  Serper — 2500 free/month, used only if Tavily fails or has no key.

needs_search() now covers three categories instead of a flat keyword list:
  1. Fixed topic vocabulary (sports leagues, crypto, weather, etc.)
  2. Temporal markers (today, now, this week, latest, currently...)
  3. Event/status question patterns ("who's playing", "how did X go",
     "what happened to X", "is X still Y") — these catch casual phrasing
     that a fixed keyword list always misses, e.g. "how Germany got
     eliminated today" or "what's happening with Ronaldo".

Any one match is enough to trigger a search — better to over-search a few
extra cheap/casual messages than to let the model guess on something
live.
"""

import os
import re
import logging
import httpx

logger = logging.getLogger(__name__)

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
SERPER_KEY = os.getenv("SERPER_KEY", "") or os.getenv("SEARCH_API_KEY", "")


# ── 1. Fixed topic vocabulary — things that are ALWAYS time-sensitive ─────────
_TOPIC_WORDS = re.compile(
    r"\b("
    r"score|scores|result|results|fixture|fixtures|match|matches|standings|table|"
    r"transfer|transfers|lineup|squad|coach|manager|goal|goals|eliminated|qualif\w*|"
    r"world cup|wc ?26|wc ?2026|euro ?2026|champions league|premier league|"
    r"la liga|serie a|bundesliga|ligue 1|"
    r"nba|nfl|nhl|mlb|formula 1|f1|ufc|boxing|tennis|cricket|"
    r"bitcoin|btc|ethereum|eth|crypto|cryptocurrency|"
    r"price|prices|stock|nasdaq|s&p|dow|market|markets|"
    r"exchange rate|dollar|euro|usd|eur|gbp|ruble|som|"
    r"weather|forecast|temperature|rain|snow|"
    r"election|elections|president|prime minister|government|war|conflict|"
    r"died|death|arrested|married|engaged|"
    r"release|released|version|update|patch|launch|launched"
    r")\b",
    re.IGNORECASE,
)

# ── 2. Temporal markers — "this is happening NOW" signals ─────────────────────
_TEMPORAL_WORDS = re.compile(
    r"\b("
    r"today|tonight|tomorrow|yesterday|this week|this weekend|right now|"
    r"currently|latest|breaking|trending|viral|live|ongoing|so far|"
    r"now|these days|recently|just happened|just announced"
    r")\b",
    re.IGNORECASE,
)

# ── 3. Event/status question PATTERNS — catches casual real-world phrasing ────
# These match how people actually ask about live/current things without
# needing the topic word itself to appear in a fixed list.
_EVENT_PATTERNS = [
    re.compile(r"\bhow('?s| is| did)\b.{0,30}\b(go|going|going on|doing|done)\b", re.I),
    re.compile(r"\bwhat('?s| is)\b.{0,20}\b(happening|going on|the latest|new)\b", re.I),
    re.compile(r"\bwho('?s| is)\b.{0,20}\b(playing|winning|losing|leading)\b", re.I),
    re.compile(r"\b(any|got)\s+(news|updates?)\b", re.I),
    re.compile(r"\bis\s+\w+\s+still\b", re.I),                      # "is X still Y"
    re.compile(r"\bwhat happened to\b", re.I),
    re.compile(r"\bdid\s+\w+\s+(win|lose|happen|get)\b", re.I),     # "did Germany win"
]


def needs_search(text: str) -> bool:
    if _TOPIC_WORDS.search(text):
        return True
    if _TEMPORAL_WORDS.search(text):
        return True
    for pattern in _EVENT_PATTERNS:
        if pattern.search(text):
            return True
    return False


# ── Tavily (primary) ──────────────────────────────────────────────────────────

async def _tavily_search(query: str) -> str | None:
    if not TAVILY_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": TAVILY_KEY,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": 4,
                },
            )
        if resp.status_code != 200:
            logger.warning(f"Tavily HTTP {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        parts = []
        if answer := data.get("answer"):
            parts.append(f"Summary: {answer}")
        for r in data.get("results", [])[:4]:
            content = (r.get("content") or "")[:250]
            if content:
                parts.append(f"- {r.get('title','')}: {content}")

        return "\n".join(parts) if parts else None

    except Exception as e:
        logger.warning(f"Tavily search exception: {e}")
        return None


# ── Serper (backup) ───────────────────────────────────────────────────────────

async def _serper_search(query: str) -> str | None:
    if not SERPER_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": query, "num": 4},
            )
        if resp.status_code != 200:
            logger.warning(f"Serper HTTP {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        snippets = []
        if ab := data.get("answerBox"):
            if ans := ab.get("answer") or ab.get("snippet"):
                snippets.append(f"Summary: {ans}")
        if kg := data.get("knowledgeGraph", {}).get("description"):
            snippets.append(f"Info: {kg[:200]}")
        for r in data.get("organic", [])[:4]:
            if s := r.get("snippet"):
                snippets.append(f"- {r.get('title','')}: {s}")

        return "\n".join(snippets) if snippets else None

    except Exception as e:
        logger.warning(f"Serper search exception: {e}")
        return None


# ── Main entry point ──────────────────────────────────────────────────────────

async def web_search(query: str) -> str | None:
    """
    Try Tavily first, fall back to Serper.
    Returns a clean text block, or None if both fail / no keys configured.
    """
    result = await _tavily_search(query)
    if result:
        logger.info(f"Search OK via Tavily: {query[:50]!r}")
        return result

    result = await _serper_search(query)
    if result:
        logger.info(f"Search OK via Serper (Tavily fallback): {query[:50]!r}")
        return result

    if not TAVILY_KEY and not SERPER_KEY:
        logger.warning("No search API keys configured (TAVILY_API_KEY / SERPER_KEY)")
    else:
        logger.warning(f"Both search sources failed for: {query[:50]!r}")

    return None
