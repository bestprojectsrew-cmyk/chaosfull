"""
providers.py — Multi-provider LLM router with automatic fallback.

Provider priority (fastest/cheapest first):
  1. Groq       — ultra-fast, free tier, best for most requests
  2. Gemini     — Google free tier, good fallback
  3. OpenRouter — aggregator, many free models

Each provider implements: async call(messages, max_tokens, temperature) -> str
Router tries them in order, skips rate-limited/failed ones, returns first success.
"""
import os
import time
import logging
import httpx
from groq import AsyncGroq

logger = logging.getLogger(__name__)

# ── Model choices per task type ───────────────────────────────────────────────
GROQ_MODELS = {
    "default":  "openai/gpt-oss-120b",    # best available on Groq (Jun 2026)
    "fast":     "openai/gpt-oss-20b",     # fast/cheap for greetings + memory
    "memory":   "openai/gpt-oss-20b",     # cheap+fast for memory extraction
}

GEMINI_MODELS = {
    "default": "gemini-1.5-flash",
    "fast":    "gemini-1.5-flash-8b",
}

OPENROUTER_MODELS = {
    "default": "mistralai/mistral-7b-instruct:free",
    "fast":    "mistralai/mistral-7b-instruct:free",
}

# ── Circuit breaker state ─────────────────────────────────────────────────────
_failures: dict[str, dict] = {}
_COOLDOWN = 60   # seconds before retrying a failed provider


def _is_available(name: str) -> bool:
    state = _failures.get(name, {})
    if not state:
        return True
    if time.time() - state.get("since", 0) > _COOLDOWN:
        _failures.pop(name, None)
        return True
    return False


def _mark_failed(name: str) -> None:
    _failures[name] = {"since": time.time()}
    logger.warning(f"Provider {name} marked as unavailable for {_COOLDOWN}s")


def _mark_ok(name: str) -> None:
    _failures.pop(name, None)


# ── Groq provider ─────────────────────────────────────────────────────────────

_groq = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", "")) if os.getenv("GROQ_API_KEY") else None


async def _call_groq(messages: list[dict], max_tokens: int, temperature: float, tier: str = "default") -> str:
    if not _groq:
        raise RuntimeError("Groq not configured")
    model = GROQ_MODELS.get(tier, GROQ_MODELS["default"])

    kwargs = dict(
        model=model, messages=messages,
        max_tokens=max_tokens, temperature=temperature,
    )
    # gpt-oss models are reasoning models — force low effort + hidden reasoning
    # so chain-of-thought never leaks into the visible reply (no more <think> blocks)

    resp = await _groq.chat.completions.create(**kwargs)
    return resp.choices[0].message.content.strip()


# ── Gemini provider ───────────────────────────────────────────────────────────

_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


async def _call_gemini(messages: list[dict], max_tokens: int, temperature: float, tier: str = "default") -> str:
    if not _GEMINI_KEY:
        raise RuntimeError("Gemini not configured")

    model = GEMINI_MODELS.get(tier, GEMINI_MODELS["default"])

    # Convert OpenAI-style messages to Gemini format
    system_text = ""
    contents = []
    for m in messages:
        if m["role"] == "system":
            system_text = m["content"]
        elif m["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": m["content"]}]})
        elif m["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": m["content"]}]})

    payload: dict = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }
    if system_text:
        payload["systemInstruction"] = {"parts": [{"text": system_text}]}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            _GEMINI_URL.format(model=model),
            params={"key": _GEMINI_KEY},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# ── OpenRouter provider ───────────────────────────────────────────────────────

_OR_KEY = os.getenv("OPENROUTER_API_KEY", "")


async def _call_openrouter(messages: list[dict], max_tokens: int, temperature: float, tier: str = "default") -> str:
    if not _OR_KEY:
        raise RuntimeError("OpenRouter not configured")

    model = OPENROUTER_MODELS.get(tier, OPENROUTER_MODELS["default"])

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {_OR_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature},
        )
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"].strip()


# ── Router ────────────────────────────────────────────────────────────────────

_PROVIDERS = [
    ("groq",       _call_groq),
    ("openrouter", _call_openrouter),
]


async def chat(
    messages: list[dict],
    max_tokens: int = 400,
    temperature: float = 0.85,
    tier: str = "default",
) -> str:
    """
    Try providers in order. Return first successful response.
    Raises RuntimeError only if ALL providers fail.
    """
    last_error = None
    for name, fn in _PROVIDERS:
        if not _is_available(name):
            continue
        try:
            result = await fn(messages, max_tokens, temperature, tier)
            _mark_ok(name)
            return result
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower() or "quota" in err.lower():
                _mark_failed(name)
                logger.info(f"{name} rate-limited, trying next")
            elif "not configured" in err.lower():
                logger.info(f"{name} skipped — no API key set")
            else:
                _mark_failed(name)
                logger.warning(f"{name} error: {e}")
            last_error = f"{name}: {e}"

    raise RuntimeError(f"All LLM providers failed. {last_error}")
