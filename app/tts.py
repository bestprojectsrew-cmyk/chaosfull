"""
tts.py — Text to speech using gTTS (Google, free, no API key needed).
"""
import os
import logging
import tempfile
import asyncio
from gtts import gTTS

logger = logging.getLogger(__name__)

# Language code map for gTTS
LANG_MAP = {
    "en": "en", "ru": "ru", "uz": "uz",
    "tr": "tr", "ar": "ar", "de": "de",
    "fr": "fr", "es": "es", "ko": "ko",
    "ja": "ja", "it": "it", "uk": "uk",
}


async def text_to_voice(text: str, lang_code: str = "en") -> bytes | None:
    """Convert text to mp3 bytes using gTTS."""
    gtts_lang = LANG_MAP.get(lang_code, "en")
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name

        def _generate():
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(tmp_path)

        # Run in thread to avoid blocking event loop
        await asyncio.get_event_loop().run_in_executor(None, _generate)

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        os.unlink(tmp_path)
        logger.info(f"[tts] generated {len(audio_bytes)} bytes in {gtts_lang}")
        return audio_bytes

    except Exception as e:
        logger.warning(f"[tts] failed: {e}")
        return None


async def send_voice_reply(update, audio_bytes: bytes) -> bool:
    """Send audio bytes as a Telegram voice message."""
    try:
        import io
        await update.message.reply_voice(voice=io.BytesIO(audio_bytes))
        return True
    except Exception as e:
        logger.warning(f"[tts] send failed: {e}")
        return False
