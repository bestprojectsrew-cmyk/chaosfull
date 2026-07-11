"""
voice.py — Transcribe Telegram voice messages using Groq Whisper (free).
"""
import os
import logging
import tempfile
import httpx

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


async def transcribe_voice(file_bytes: bytes, mime_type: str = "audio/ogg") -> str | None:
    """
    Send voice bytes to Groq Whisper API.
    Returns transcribed text or None if failed.
    """
    if not GROQ_API_KEY:
        logger.warning("[voice] GROQ_API_KEY not set")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": ("voice.ogg", file_bytes, mime_type)},
                data={"model": "whisper-large-v3-turbo", "response_format": "text"},
            )
        if resp.status_code == 200:
            text = resp.text.strip()
            logger.info(f"[voice] transcribed: {text[:60]!r}")
            return text
        else:
            logger.warning(f"[voice] Whisper HTTP {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"[voice] transcription failed: {e}")
        return None