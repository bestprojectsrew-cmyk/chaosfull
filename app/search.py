"""
search.py — Multi-source web search with automatic waterfall fallback.

Search chain (tried in order until one succeeds):
  1. Gemini Search Grounding  — free, built into Gemini API, no quota limits
  2. Serper.dev               — 2500 free/month, fast, Google results
  3. Brave Search API         — 2000 free/month, independent index
  4. SerpApi                  — 100 free/month
  5. DuckDuckGo               — completely free, no key, no limit (rate-limited but always works)

Each source is tried in order. First success wins. User never sees failures.
If ALL fail (extremely unlikely), bot answers from training knowledge + says it couldn't verify.
"""

import os
import re
import time
import logging
import httpx

logger = logging.getLogger(__name__)

# ── API keys (all optional — bot works with zero keys via DuckDuckGo) ─────────
GEMINI_KEY     = os.getenv("GEMINI_API_KEY", "")
SERPER_KEY     = os.getenv("SEARCH_API_KEY", "") or os.getenv("SERPER_KEY", "")
BRAVE_KEY      = os.getenv("BRAVE_API_KEY", "")
SERPAPI_KEY    = os.getenv("SERPAPI_KEY", "")

# ── Circuit breaker per source ─────────────────────────────────────────────────
_cb: dict[str, float] = {}   # source → timestamp when it failed
_CB_COOLDOWN = 300           # 5 min cooldown after a source fails


def _available(name: str) -> bool:
    t = _cb.get(name, 0)
    if t and time.time() - t < _CB_COOLDOWN:
        return False
    return True


def _fail(name: str) -> None:
    _cb[name] = time.time()
    logger.info(f"Search source '{name}' marked unavailable for {_CB_COOLDOWN}s")


def _ok(name: str) -> None:
    _cb.pop(name, None)


# ── Topic detection — which messages need live search ─────────────────────────
_TRIGGERS = re.compile(
    r"\b("
    # Sports
    r"score|scores|result|results|fixture|fixtures|match|matches|standings|table|"
    r"transfer|transfers|lineup|squad|coach|manager|goal|goals|"
    r"world cup|wc 26|wc26|wc 2026|euro 2026|champions league|premier league|la liga|serie a|bundesliga|ligue 1|"
    r"nba|nfl|nhl|mlb|formula 1|f1|ufc|boxing|tennis|cricket|"
    # Crypto & finance
    r"bitcoin|btc|ethereum|eth|crypto|cryptocurrency|"
    r"price|prices|stock|nasdaq|s&p|dow|market|markets|"
    r"exchange rate|dollar|euro|usd|eur|gbp|ruble|som|"
    # Weather
    r"weather|forecast|temperature|rain|snow|"
    # News & politics
    r"election|elections|president|prime minister|government|war|conflict|"
    r"breaking|latest|news|today|yesterday|this week|right now|currently|"
    r"died|death|arrested|married|"
    # Tech
    r"release|released|version|update|patch|launch|launched|"
    # General current events
    r"trending|viral|meme|going on|happening|whats up with|how is|"
    r"product price|how much does|how much is"
    r")\b",
    re.IGNORECASE,
)


def needs_search(text: str) -> bool:
    return bool(_TRIGGERS.search(text))


# ── 1. Gemini Search Grounding ────────────────────────────────────────────────

async def _gemini_search(query: str) -> str | None:
    """
    Uses Gemini's built-in Google Search grounding.
    Free with Gemini API key. No separate quota.
    Returns search-grounded text summary.
    """
    if not GEMINI_KEY or not _available("gemini_search"):
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": GEMINI_KEY},
                json={
                    "contents": [{"parts": [{"text": f"Search and summarize briefly: {query}"}]}],
                    "tools": [{"google_search": {}}],
                    "generationConfig": {"maxOutputTokens": 300, "temperature": 0.1},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if text:
                _ok("gemini_search")
                return f"[Gemini Search] {text[:800]}"
    except Exception as e:
        logger.debug(f"Gemini search failed: {e}")
        _fail("gemini_search")
    return None


# ── 2. Serper.dev ─────────────────────────────────────────────────────────────

async def _serper_search(query: str) -> str | None:
    """2500 free searches/month. Fast, Google results."""
    if not SERPER_KEY or not _available("serper"):
        return None
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": query, "num": 4},
            )
            resp.raise_for_status()
            data = resp.json()

        snippets = []
        if ab := data.get("answerBox"):
            if ans := ab.get("answer") or ab.get("snippet"):
                snippets.append(f"Direct: {ans}")
        if kg := data.get("knowledgeGraph", {}).get("description"):
            snippets.append(f"Info: {kg[:200]}")
        for r in data.get("organic", [])[:3]:
            if s := r.get("snippet"):
                snippets.append(f"{r.get('title','')}: {s}")

        if snippets:
            _ok("serper")
            return "\n".join(snippets)
        _fail("serper")
    except Exception as e:
        err = str(e)
        if "403" in err or "429" in err or "quota" in err.lower():
            _fail("serper")
        logger.debug(f"Serper failed: {e}")
    return None


# ── 3. Brave Search API ───────────────────────────────────────────────────────

async def _brave_search(query: str) -> str | None:
    """2000 free queries/month. Independent index."""
    if not BRAVE_KEY or not _available("brave"):
        return None
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_KEY},
                params={"q": query, "count": 4, "search_lang": "en"},
            )
            resp.raise_for_status()
            data = resp.json()

        snippets = []
        for r in data.get("web", {}).get("results", [])[:4]:
            if s := r.get("description"):
                snippets.append(f"{r.get('title','')}: {s}")

        if snippets:
            _ok("brave")
            return "\n".join(snippets)
        _fail("brave")
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            _fail("brave")
        logger.debug(f"Brave search failed: {e}")
    return None


# ── 4. SerpApi ────────────────────────────────────────────────────────────────

async def _serpapi_search(query: str) -> str | None:
    """100 free searches/month."""
    if not SERPAPI_KEY or not _available("serpapi"):
        return None
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={"q": query, "api_key": SERPAPI_KEY, "num": 4, "engine": "google"},
            )
            resp.raise_for_status()
            data = resp.json()

        snippets = [
            f"{r.get('title','')}: {r.get('snippet','')}"
            for r in data.get("organic_results", [])[:4]
            if r.get("snippet")
        ]
        if snippets:
            _ok("serpapi")
            return "\n".join(snippets)
        _fail("serpapi")
    except Exception as e:
        if "429" in str(e):
            _fail("serpapi")
        logger.debug(f"SerpApi failed: {e}")
    return None


# ── 5. DuckDuckGo (always-free fallback) ─────────────────────────────────────

async def _ddg_search(query: str) -> str | None:
    """
    No API key. No quota. Always available.
    Uses duckduckgo-search library (runs sync in thread to avoid blocking).
    """
    if not _available("ddg"):
        return None
    try:
        import asyncio
        from duckduckgo_search import DDGS

        def _sync_search():
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=4))
            return results

        results = await asyncio.get_event_loop().run_in_executor(None, _sync_search)
        snippets = [
            f"{r.get('title','')}: {r.get('body','')[:200]}"
            for r in results if r.get("body")
        ]
        if snippets:
            _ok("ddg")
            return "\n".join(snippets)
    except Exception as e:
        logger.debug(f"DDG failed: {e}")
        _fail("ddg")
    return None


# ── Main search function — waterfall ─────────────────────────────────────────

_SOURCES = [
    ("Gemini Search",  _gemini_search),
    ("Serper",         _serper_search),
    ("Brave",          _brave_search),
    ("SerpApi",        _serpapi_search),
    ("DuckDuckGo",     _ddg_search),
]


async def web_search(query: str) -> str | None:
    """
    Try all search sources in order. Return first successful result.
    Returns None only if every single source fails (extremely unlikely).
    """
    for name, fn in _SOURCES:
        if not _available(name.lower().replace(" ", "_")):
            continue
        try:
            result = await fn(query)
            if result:
                logger.info(f"Search succeeded via {name}")
                return result
        except Exception as e:
            logger.debug(f"{name} exception: {e}")

    logger.warning("All search sources failed for query: " + query[:60])
    return None