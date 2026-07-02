"""
queue_manager.py — Global async AI request queue.

Limits concurrent AI provider calls so free-tier rate limits
aren't hammered when many users message simultaneously.

Config (via env vars):
  AI_MAX_CONCURRENT  — max simultaneous provider calls (default: 6)
  AI_QUEUE_SIZE      — max queued requests before rejecting (default: 200)

Flow:
  User message → queue_manager.submit(call_fn) → semaphore → provider
                                                ↓
                              if queue full → friendly rejection message
                                                ↓
                              result returned to user
"""

import asyncio
import logging
import os
import time

logger = logging.getLogger(__name__)

MAX_CONCURRENT = int(os.getenv("AI_MAX_CONCURRENT", "6"))
MAX_QUEUE      = int(os.getenv("AI_QUEUE_SIZE", "200"))

_semaphore  = asyncio.Semaphore(MAX_CONCURRENT)
_queue_size = 0
_total_processed = 0
_total_rejected  = 0

QUEUE_FULL_MSG = (
    "🧠 Chaoz is getting a lot of messages right now. "
    "Give me a few seconds and try again."
)


async def submit(call_fn) -> str:
    """
    Submit an AI call to the queue.
    Returns the result string or a queue-full message.
    """
    global _queue_size, _total_processed, _total_rejected

    if _queue_size >= MAX_QUEUE:
        _total_rejected += 1
        logger.warning(f"[queue] FULL ({_queue_size}/{MAX_QUEUE}) — rejecting request")
        return QUEUE_FULL_MSG

    _queue_size += 1
    start = time.time()

    try:
        async with _semaphore:
            wait_time = time.time() - start
            if wait_time > 1.0:
                logger.info(f"[queue] request waited {wait_time:.1f}s in queue")
            result = await call_fn()
            _total_processed += 1
            elapsed = time.time() - start
            logger.info(f"[queue] request done in {elapsed:.1f}s | processed={_total_processed}")
            return result
    except Exception as e:
        logger.error(f"[queue] call_fn raised: {e}")
        raise
    finally:
        _queue_size -= 1


def stats() -> dict:
    return {
        "queue_size":       _queue_size,
        "max_concurrent":   MAX_CONCURRENT,
        "max_queue":        MAX_QUEUE,
        "total_processed":  _total_processed,
        "total_rejected":   _total_rejected,
        "semaphore_locked": MAX_CONCURRENT - _semaphore._value,
    }
