"""
language.py — Language detection + vibe-aware translation instructions
"""
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 42

LANG_MAP = {
    "uz": "Uzbek",   "ru": "Russian",  "en": "English",
    "tr": "Turkish", "ar": "Arabic",   "de": "German",
    "fr": "French",  "es": "Spanish",  "zh": "Chinese",
    "ko": "Korean",  "ja": "Japanese", "it": "Italian",
    "pt": "Portuguese", "hi": "Hindi", "fa": "Farsi",
    "kk": "Kazakh",  "uk": "Ukrainian",
}

UZBEK_STRONG_KEYWORDS = {
    "salom", "qanday", "nima", "yoq", "rahmat", "xayr", "kerak",
    "emas", "chunki", "qilib", "o'zbek", "o'zbekcha", "uzbek",
    "toshkent", "namangan", "samarqand", "andijon", "qanaqa",
    "qayerda", "qachon", "yangilik", "ketaman", "boramiz",
    "ko'ramiz", "ko'rib", "bo'ladi", "bo'lsa", "bo'ldi",
    "qildim", "qilaman", "hozir", "bugun", "ertaga", "kecha",
}

# Vibe examples per language — tells LLM how to sound, not just what to say
LANG_VIBE = {
    "en": "English. Use Gen Z slang: bro, fr, no cap, lowkey, bussin, cooked, W, L, ngl, npc, sigma, rizz, skibidi, delulu, brainrot, ong, bet, finna, aura.",
    "uz": "Uzbek. Use Uzbek internet slang: aka, opa, bro, jon, zo'r, zo'rmi, nima gap, yoq eeee, voy, axir, bo'pti, hmm, shu degani, kayfiyat, opa/aka (for respect). Sound like an Uzbek Gen Z on Telegram.",
    "ru": "Russian. Use Russian internet slang: бро, чел, ну и что, да ладно, серьезно, вот это да, норм, жиза, имба, ору, кринж, лол, рофл, го, ок, топ, дно. Sound like Russian Gen Z on VK/Telegram.",
    "tr": "Turkish. Use Turkish Gen Z slang: ya, abi, kanka, bro, haha, vay be, gerçekten mi, ya ne, süper, rezil, kötü. Sound like Turkish Gen Z on social media.",
    "ar": "Arabic. Sound like Arab Gen Z online. Use casual Arabic, maybe some English slang mixed in.",
    "ko": "Korean. Sound like Korean Gen Z online with natural Korean internet expressions.",
    "ja": "Japanese. Sound like Japanese Gen Z online with casual Japanese.",
    "de": "German. Sound like German Gen Z online with casual German slang.",
    "fr": "French. Sound like French Gen Z online with casual French slang.",
    "es": "Spanish. Sound like Spanish/Latin American Gen Z online with casual Spanish slang.",
    "kk": "Kazakh. Sound like Kazakh Gen Z online.",
    "uk": "Ukrainian. Sound like Ukrainian Gen Z online.",
}


def _uzbek_heuristic(text: str) -> bool:
    words = set(text.lower().split())
    return len(words & UZBEK_STRONG_KEYWORDS) >= 1


def detect_language(text: str) -> tuple[str, str]:
    if _uzbek_heuristic(text):
        return "uz", "Uzbek"
    try:
        code = detect(text)
        if code.startswith("zh"):
            code = "zh"
        if code in ("so", "tl", "sw", "mg") and _uzbek_heuristic(text):
            return "uz", "Uzbek"
        label = LANG_MAP.get(code, "English")
        if code not in LANG_MAP:
            return "en", "English"
        return code, label
    except LangDetectException:
        if _uzbek_heuristic(text):
            return "uz", "Uzbek"
        return "en", "English"


def get_lang_instruction(lang_code: str, lang_label: str) -> str:
    vibe = LANG_VIBE.get(lang_code, f"{lang_label}. Match the local Gen Z internet vibe.")
    return (
        f"LANGUAGE RULE: Respond ONLY in {vibe} "
        f"Do NOT translate literally. TRANSLATE THE VIBE. "
        f"If the user switches language mid-convo, you switch too instantly."
    )
