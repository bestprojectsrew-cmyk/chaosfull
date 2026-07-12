"""
tts.py — Text to speech using edge-tts (free, no API key needed).
Converts text to voice message and sends it to Telegram.
"""
import os
import asyncio
import logging
import tempfile
import edge_tts

logger = logging.getLogger(__name__)

# Voice map per language — natural sounding voices
VOICE_MAP = {
    "en": "en-US-ChristopherNeural",
    "ru": "ru-RU-DmitryNeural",
    "uz": "uz-UZ-MadinaNeural",
    "tr": "tr-TR-AhmetNeural",
    "ar": "ar-SA-HamedNeural",
    "de": "de-DE-ConradNeural",
    "fr": "fr-FR-HenriNeural",
    "es": "es-ES-AlvaroNeural",
    "ko": "ko-KR-InJoonNeural",
    "ja": "ja-JP-KeitaNeural",
}

DEFAULT_VOICE = "en-US-ChristopherNeural"


async def text_to_voice(text: str, lang_code: str = "en") -> bytes | None:
    """
    Convert text to audio bytes using edge-tts.
    Returns mp3 bytes or None if failed.
    """
    voice = VOICE_MAP.get(lang_code, DEFAULT_VOICE)
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        os.unlink(tmp_path)
        return audio_bytes

    except Exception as e:
        logger.warning(f"[tts] failed: {e}")
        return None


async def send_voice_reply(update, audio_bytes: bytes) -> bool:
    """Send audio bytes as a Telegram voice message. Returns True if sent."""
    try:
        import io
        await update.message.reply_voice(voice=io.BytesIO(audio_bytes))
        return True
    except Exception as e:
        logger.warning(f"[tts] send failed: {e}")
        return False
