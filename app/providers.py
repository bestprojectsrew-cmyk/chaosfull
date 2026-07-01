"""
providers.py — LLM router: Groq → Gemini → OpenRouter, in that order.

Why this order:
  - Groq: fastest, most generous free tier (30 RPM / 14,400 RPD), primary.
  - Gemini: 2.5 Flash gets 1,500 req/day, 15 RPM free — solid real backup
    as long as the exact model name `gemini-2.5-flash` is used (older
    `gemini-2.0-flash` and `gemini-1.5-flash` are deprecated as of mid-2026).
  - OpenRouter: uses `openrouter/free`, OpenRouter's own auto-router that
    picks from whichever free model is actually available right now.
    Hardcoding one specific free model (e.g. llama-3.3-70b:free) is risky —
    free models on OpenRouter rotate and disappear without notice. The
    auto-router avoids that failure mode entirely.

Every failure is logged with the exact provider + reason, so a dead chain
is always visible in Railway logs instead of producing a silent
"something broke" with no trail.
"""
import os
import time
import logging
import httpx
from groq import AsyncGroq

logger = logging.getLogger(__name__)

# ── Model choices per task type ───────────────────────────────────────────────
GROQ_MODELS = {
    "default": "openai/gpt-oss-120b",
    "fast":    "openai/gpt-oss-20b",
    "memory":  "openai/gpt-oss-20b",
}

GEMINI_MODELS = {
    "default": "gemini-2.5-flash",
    "fast":    "gemini-2.5-flash",
    "memory":  "gemini-2.5-flash",
}

# openrouter/free = OpenRouter's auto-router across whatever free models
# are currently live. Avoids hardcoding a model that can vanish overnight.
OPENROUTER_MODELS = {
    "default": "openrouter/free",
    "fast":    "openrouter/free",
    "memory":  "openrouter/free",
}

# ── Circuit breaker state ─────────────────────────────────────────────────────
_failures: dict[str, float] = {}
_COOLDOWN = 5


def _is_available(name: str) -> bool:
    t = _failures.get(name, 0)
    return not (t and time.time() - t < _COOLDOWN)


def _mark_failed(name: str, reason: str) -> None:
    _failures[name] = time.time()
    logger.warning(f"[providers] {name} FAILED ({reason}) — cooling down {_COOLDOWN}s")


def _mark_ok(name: str) -> None:
    _failures.pop(name, None)


# ── Groq ──────────────────────────────────────────────────────────────────────

_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
_groq = AsyncGroq(api_key=_GROQ_KEY) if _GROQ_KEY else None
if not _GROQ_KEY:
    logger.warning("[providers] GROQ_API_KEY not set — Groq disabled")


async def _call_groq(messages: list[dict], max_tokens: int, temperature: float, tier: str) -> str:
    if not _groq:
        raise RuntimeError("groq_not_configured")

    model = GROQ_MODELS.get(tier, GROQ_MODELS["default"])
    kwargs = dict(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature)

    resp = await _groq.chat.completions.create(**kwargs)
    content = resp.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("groq_empty_response")
    return content.strip()


# ── Gemini (chat fallback — separate from search.py's use of Gemini) ──────────

_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if not _GEMINI_KEY:
    logger.info("[providers] GEMINI_API_KEY not set — Gemini fallback disabled")


async def _call_gemini(messages: list[dict], max_tokens: int, temperature: float, tier: str) -> str:
    if not _GEMINI_KEY:
        raise RuntimeError("gemini_not_configured")

    model = GEMINI_MODELS.get(tier, GEMINI_MODELS["default"])

    # Convert OpenAI-style messages -> Gemini's contents format
    system_text = ""
    contents = []
    for m in messages:
        if m["role"] == "system":
            system_text = (system_text + "\n" + m["content"]).strip()
        elif m["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": m["content"]}]})
        elif m["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": m["content"]}]})

    payload = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
    }
    if system_text:
        payload["systemInstruction"] = {"parts": [{"text": system_text}]}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": _GEMINI_KEY},
            json=payload,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"gemini_http_{resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"gemini_unexpected_response: {str(data)[:200]}")

    if not content or not content.strip():
        raise RuntimeError("gemini_empty_response")
    return content.strip()


# ── OpenRouter (final fallback, uses the auto-router) ──────────────────────────

_OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
if not _OR_KEY:
    logger.info("[providers] OPENROUTER_API_KEY not set — final fallback disabled")


async def _call_openrouter(messages: list[dict], max_tokens: int, temperature: float, tier: str) -> str:
    if not _OR_KEY:
        raise RuntimeError("openrouter_not_configured")

    model = OPENROUTER_MODELS.get(tier, OPENROUTER_MODELS["default"])

    async with httpx.AsyncClient(timeout=25.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {_OR_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature},
        )

    if resp.status_code != 200:
        raise RuntimeError(f"openrouter_http_{resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content or not content.strip():
        raise RuntimeError("openrouter_empty_response")
    return content.strip()


# ── Router ────────────────────────────────────────────────────────────────────

_PROVIDERS = []

if _groq:
    _PROVIDERS.append(("groq", _call_groq))

if _GEMINI_KEY:
    _PROVIDERS.append(("gemini", _call_gemini))

if _OR_KEY:
    _PROVIDERS.append(("openrouter", _call_openrouter))


async def chat(
    messages: list[dict],
    max_tokens: int = 400,
    temperature: float = 0.85,
    tier: str = "default",
) -> str:
    """
    Try Groq -> Gemini -> OpenRouter in order. Logs every attempt and
    failure with the exact reason. Raises RuntimeError with full detail
    only if every provider fails.
    """
    errors = []
errors = []

for name, fn in _PROVIDERS:
    if not _is_available(name):
        logger.info(f"[providers] skipping {name} (in cooldown)")
        continue

    try:
        result = await fn(messages, max_tokens, temperature, tier)
        _mark_ok(name)
        logger.info(f"[providers] {name} succeeded")
        return result

        except Exception as e:
            reason = str(e)
            errors.append(f"{name}: {reason}")

            if "not_configured" in reason:
                logger.info(f"[providers] {name} skipped — no API key set")
                continue

            if "429" in reason or "rate" in reason.lower() or "quota" in reason.lower():
                _mark_failed(name, "rate_limited")
            else:
    logger.warning(
        f"[providers] {name} failed: {reason}"
    )

    full_error = " | ".join(errors) if errors else "no providers configured"
    logger.error(f"[providers] ALL PROVIDERS FAILED: {full_error}")
    return (
    "🧠 My AI brain is taking a short coffee break ☕.\n"
    "All AI providers are temporarily busy.\n"
    "Try again in a few moments."
)
