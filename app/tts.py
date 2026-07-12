"""
tts.py — Text to speech using Groq Orpheus TTS (free, natural sounding).
Falls back to gTTS if Groq TTS fails.
"""
import os
import io
import logging
import tempfile
import asyncio
import httpx

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Groq Orpheus only supports English and Arabic currently
GROQ_TTS_LANGS = {"en", "ar"}

# Voice per language for Groq
GROQ_VOICES = {
    "en": "fritz-playai",
    "ar": "ahmad-playai",
}

# gTTS language map as fallback for other languages
GTTS_LANG_MAP = {
    "ru": "ru", "uz": "uz", "tr": "tr", "de": "de",
    "fr": "fr", "es": "es", "ko": "ko", "ja": "ja",
    "it": "it", "uk": "uk", "en": "en",
}


async def _groq_tts(text: str, lang_code: str) -> bytes | None:
    """Use Groq Orpheus TTS — natural sounding, free tier."""
    if not GROQ_API_KEY:
        return None
    voice = GROQ_VOICES.get(lang_code, "fritz-playai")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "playai-tts",
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3",
                },
            )
        if resp.status_code == 200:
            logger.info(f"[tts] Groq TTS success, {len(resp.content)} bytes")
            return resp.content
        else:
            logger.warning(f"[tts] Groq TTS HTTP {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"[tts] Groq TTS failed: {e}")
        return None


async def _gtts_tts(text: str, lang_code: str) -> bytes | None:
    """Fallback: gTTS for non-English languages."""
    try:
        from gtts import gTTS
        gtts_lang = GTTS_LANG_MAP.get(lang_code, "en")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp_path = f.name

        def _generate():
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(tmp_path)

        await asyncio.get_event_loop().run_in_executor(None, _generate)

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp_path)
        logger.info(f"[tts] gTTS fallback success, {len(audio_bytes)} bytes")
        return audio_bytes
    except Exception as e:
        logger.warning(f"[tts] gTTS failed: {e}")
        return None


MAX_TTS_CHARS = 200  # keep voice replies short and natural

async def text_to_voice(text: str, lang_code: str = "en") -> bytes | None:
    """
    Convert text to audio bytes.
    Trims to MAX_TTS_CHARS so voice replies stay short.
    Uses Groq Orpheus for English/Arabic (natural).
    Falls back to gTTS for other languages.
    """
    # Trim to keep voice short and natural
    if len(text) > MAX_TTS_CHARS:
        # Cut at last sentence end within limit
        trimmed = text[:MAX_TTS_CHARS]
        for punct in (".", "!", "?", "😭", "💀"):
            idx = trimmed.rfind(punct)
            if idx > 80:
                trimmed = trimmed[:idx + 1]
                break
        text = trimmed

    # Try Groq TTS first for supported languages
    if lang_code in GROQ_TTS_LANGS:
        audio = await _groq_tts(text, lang_code)
        if audio:
            return audio

    # Fallback to gTTS
    return await _gtts_tts(text, lang_code)

async def send_voice_reply(update, audio_bytes: bytes) -> bool:
    """Send audio bytes as a Telegram voice message."""
    try:
        await update.message.reply_voice(voice=io.BytesIO(audio_bytes))
        return True
    except Exception as e:
        logger.warning(f"[tts] send failed: {e}")
        return False
