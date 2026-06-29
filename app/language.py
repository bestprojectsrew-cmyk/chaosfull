"""
language.py — Language detection. Simple, reliable, no overengineering.
"""
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 42

LANG_LABELS = {
    "uz": "Uzbek", "ru": "Russian", "en": "English", "tr": "Turkish",
    "ar": "Arabic", "de": "German", "fr": "French", "es": "Spanish",
    "zh": "Chinese", "ko": "Korean", "ja": "Japanese", "it": "Italian",
    "pt": "Portuguese", "hi": "Hindi", "fa": "Farsi", "kk": "Kazakh",
    "uk": "Ukrainian", "pl": "Polish", "nl": "Dutch", "sv": "Swedish",
    "az": "Azerbaijani", "tg": "Tajik",
}

# Uzbek heuristic — langdetect misclassifies Uzbek as Somali/Tagalog
_UZBEK_KEYS = {
    "salom", "qanday", "nima", "yoq", "rahmat", "xayr", "kerak", "emas",
    "chunki", "qilib", "o'zbek", "toshkent", "namangan", "samarqand",
    "andijon", "qanaqa", "qayerda", "qachon", "yangilik", "ketaman",
    "bo'ladi", "bo'lsa", "bo'ldi", "qildim", "qilaman", "hozir",
    "bugun", "ertaga", "kecha", "aka", "opa",
}


def detect_language(text: str) -> tuple[str, str]:
    """
    Returns (lang_code, lang_label).
    Fast, deterministic, falls back to English on failure.
    """
    words = set(text.lower().split())
    if words & _UZBEK_KEYS:
        return "uz", "Uzbek"
    try:
        code = detect(text)
        if code.startswith("zh"):
            code = "zh"
        # langdetect misclassifies short Uzbek/Kazakh as African langs
        if code in ("so", "tl", "sw", "mg", "ny") and (words & _UZBEK_KEYS):
            return "uz", "Uzbek"
        return code, LANG_LABELS.get(code, "English")
    except LangDetectException:
        return "en", "English"
