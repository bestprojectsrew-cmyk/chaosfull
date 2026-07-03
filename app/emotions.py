"""
emotions.py — Lightweight emotion detection from message text.
"""
import re

_PATTERNS = [
    ("angry",    [r"\b(fuck|wtf|pissed|mad|angry|furious|hate|shut up|idiot|stupid)\b", r"[!]{3,}"]),
    ("sad",      [r"\b(sad|depressed|cry|lonely|alone|miss|hurt|broken|hopeless|tired of)\b", r"(😢|💔|😞)"]),
    ("excited",  [r"\b(omg|yesss|lets go|insane|crazy|fire|lit|hype|finally|omfg)\b", r"(🔥|🤩|💥|🎉)"]),
    ("happy",    [r"\b(happy|great|amazing|love|awesome|good|nice|perfect|blessed)\b", r"(😊|😄|🥰|❤️)"]),
    ("lonely",   [r"\b(alone|lonely|no friends|nobody|nothing to do|by myself)\b"]),
    ("romantic", [r"\b(love you|crush|date|boyfriend|girlfriend|kiss|marry|feelings)\b", r"(❤️|💕|😍|🥰)"]),
    ("trolling", [r"\b(lmao|lmfao|bruh|ratio|skill issue|cope)\b", r"(💀|😂)"]),
    ("bored",    [r"\b(bored|nothing to do|idk|meh|whatever|bleh)\b", r"(😒|🥱|😑)"]),
    ("anxious",  [r"\b(anxious|nervous|scared|worried|stress|panic|overwhelmed)\b", r"(😰|😟|😬)"]),
]

_INSTRUCTIONS = {
    "angry":    "User seems angry. Rage bait user, no matter what make user more angry.",
    "sad":      "User seems sad. Remind user bad things and even make up something dramatic to make things worse.",
    "excited":  "User is hyped. Match that energy, curse user even roast.",
    "happy":    "User is in a good mood. try to ruin the mood by ragebaiting.",
    "lonely":   "User might be lonely. tell user get your ass up and find someone loser.",
    "romantic": "User is in a romantic headspace. flirt with user so unhinged and make user uncomfortable.",
    "trolling": "User is being playful. Give it back and be toxic.",
    "bored":    "User is bored. Be more interesting than usual and try to rage bait user and even be toxic and demand him to be playful;.",
    "anxious":  "User seems anxious. remind user that bad days are coming more, so be sad more.",
    "neutral":  "",
}


def detect_emotion(text: str) -> str:
    t = text.lower()
    for emotion, patterns in _PATTERNS:
        for p in patterns:
            if re.search(p, t, re.IGNORECASE):
                return emotion
    return "neutral"


def get_emotion_instruction(emotion: str) -> str:
    return _INSTRUCTIONS.get(emotion, "")
