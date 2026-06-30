"""
search.py — Web search, rebuilt for reliability.

Primary: Tavily — built specifically for AI agents, 1000 free credits/month,
         returns clean structured results (not raw scraped HTML), very stable.
Backup:  Serper — 2500 free/month, used only if Tavily fails or has no key.

Why the old 5-source waterfall was scrapped: too many silent failure points,
each with different auth/quota/response formats, circuit breakers tripping
on transient errors and killing sources for 5 minutes at a time. Two solid
sources beat five flaky ones.
"""

import os
import re
import logging
import httpx

logger = logging.getLogger(__name__)

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
SERPER_KEY = os.getenv("SERPER_KEY", "") or os.getenv("SEARCH_API_KEY", "")


# ── Topic detection — which messages need live search ─────────────────────────
_TRIGGERS = re.compile(
    r"\b("
    r"score|scores|result|results|fixture|fixtures|match|matches|standings|table|"
    r"transfer|transfers|lineup|squad|coach|manager|goal|goals|"
    r"world cup|wc ?26|wc ?2026|euro ?2026|champions league|premier league|"
    r"la liga|serie a|bundesliga|ligue 1|"
    r"nba|nfl|nhl|mlb|formula 1|f1|ufc|boxing|tennis|cricket|"
    r"bitcoin|btc|ethereum|eth|crypto|cryptocurrency|"
    r"price|prices|stock|nasdaq|s&p|dow|market|markets|"
    r"exchange rate|dollar|euro|usd|eur|gbp|ruble|som|"
    r"weather|forecast|temperature|rain|snow|"
    r"election|elections|president|prime minister|government|war|conflict|"
    r"breaking|latest|news|today|yesterday|this week|right now|currently|"
    r"died|death|arrested|married|"
    r"release|released|version|update|patch|launch|launched|"
    r"trending|viral|going on|happening|whats up with|what's up with|how is|how's|"
    r"how much (does|is)"
    r")\b",
    re.IGNORECASE,
)


def needs_search(text: str) -> bool:
    return bool(_TRIGGERS.search(text))


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
            parts.append(f"Answer: {answer}")
        for r in data.get("results", [])[:4]:
            content = (r.get("content") or "")[:250]
            if content:
                parts.append(f"{r.get('title','')}: {content}")

        if parts:
            return "\n".join(parts)
        return None

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
                snippets.append(f"Direct: {ans}")
        if kg := data.get("knowledgeGraph", {}).get("description"):
            snippets.append(f"Info: {kg[:200]}")
        for r in data.get("organic", [])[:4]:
            if s := r.get("snippet"):
                snippets.append(f"{r.get('title','')}: {s}")

        return "\n".join(snippets) if snippets else None

    except Exception as e:
        logger.warning(f"Serper search exception: {e}")
        return None


# ── Main entry point ──────────────────────────────────────────────────────────

async def web_search(query: str) -> str | None:
    """
    Try Tavily first, fall back to Serper. Logs clearly which source
    succeeded or why both failed, so issues are visible in Railway logs
    instead of disappearing silently.
    """
    result = await _tavily_search(query)
    if result:
        logger.info(f"Search OK via Tavily: {query[:50]}")
        return result

    result = await _serper_search(query)
    if result:
        logger.info(f"Search OK via Serper (Tavily fallback): {query[:50]}")
        return result

    if not TAVILY_KEY and not SERPER_KEY:
        logger.warning("No search API keys configured (TAVILY_API_KEY / SERPER_KEY)")
    else:
        logger.warning(f"Both search sources failed for: {query[:50]}")

    return None
