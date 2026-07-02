"""
cache.py — In-memory response cache + duplicate request deduplication.

Cache:
  - Stores AI responses for 10 minutes by content hash.
  - Key = hash(user_message + lang_code + personality).
  - Reduces provider calls when many users ask the same thing.

Deduplication:
  - If the EXACT same request is already in-flight, wait for it
    instead of firing another provider call.
  - Example: 10 users say "hi" simultaneously → 1 provider call,
    10 users get the same response.

Both are in-memory only (no Redis needed for free-tier scale).
Automatically expires old entries every 10 minutes.
"""

import asyncio
import hashlib
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_TTL = 600  # 10 minutes


class ResponseCache:
    def __init__(self):
        self._cache: dict[str, tuple[str, float]] = {}  # key → (reply, timestamp)
        self._in_flight: dict[str, asyncio.Future] = {}  # key → Future

    def _make_key(self, user_message: str, lang_code: str, personality: str) -> str:
        raw = f"{user_message.strip().lower()}|{lang_code}|{personality}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, user_message: str, lang_code: str, personality: str) -> str | None:
        key = self._make_key(user_message, lang_code, personality)
        entry = self._cache.get(key)
        if entry:
            reply, ts = entry
            if time.time() - ts < _CACHE_TTL:
                logger.info(f"[cache] HIT for: {user_message[:40]!r}")
                return reply
            else:
                del self._cache[key]
        return None

    def set(self, user_message: str, lang_code: str, personality: str, reply: str) -> None:
        key = self._make_key(user_message, lang_code, personality)
        self._cache[key] = (reply, time.time())
        logger.info(f"[cache] SET for: {user_message[:40]!r}")

    async def get_or_call(
        self,
        user_message: str,
        lang_code: str,
        personality: str,
        call_fn,
    ) -> str:
        """
        Returns cached reply if available.
        If request is already in-flight, waits for it (dedup).
        Otherwise calls call_fn() and caches the result.
        """
        # 1. Check cache first
        cached = self.get(user_message, lang_code, personality)
        if cached:
            return cached

        key = self._make_key(user_message, lang_code, personality)

        # 2. Check if same request is already in-flight
        if key in self._in_flight:
            logger.info(f"[cache] DEDUP wait for: {user_message[:40]!r}")
            try:
                return await asyncio.wait_for(
                    asyncio.shield(self._in_flight[key]),
                    timeout=30.0,
                )
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass  # Fall through to make our own call

        # 3. Make the actual call, register as in-flight
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self._in_flight[key] = future

        try:
            result = await call_fn()
            self.set(user_message, lang_code, personality, result)
            if not future.done():
                future.set_result(result)
            return result
        except Exception as e:
            if not future.done():
                future.set_exception(e)
            raise
        finally:
            self._in_flight.pop(key, None)

    def cleanup(self) -> int:
        """Remove expired entries. Call periodically."""
        now = time.time()
        expired = [k for k, (_, ts) in self._cache.items() if now - ts >= _CACHE_TTL]
        for k in expired:
            del self._cache[k]
        if expired:
            logger.info(f"[cache] cleaned {len(expired)} expired entries")
        return len(expired)

    def stats(self) -> dict:
        return {
            "cached": len(self._cache),
            "in_flight": len(self._in_flight),
        }


# Global singleton
response_cache = ResponseCache()
