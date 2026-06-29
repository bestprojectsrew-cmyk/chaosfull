"""
emotions.py — Lightweight emotion detection from message text.
"""
import re

_PATTERNS = [
    ("angry",    [r"\b(fuck|wtf|pissed|mad|angry|furious|hate|shut up|idiot|stupid)\b", r"[!]{3,}"]),
    ("sad",      [r"\b(sad|depressed|cry|lonely|alone|miss|hurt|broken|hopeless|tired of)\b", r"(😢|😭|💔|😞)"]),
    ("excited",  [r"\b(omg|yesss|lets go|insane|crazy|fire|lit|hype|finally|omfg)\b", r"(🔥|🤩|💥|🎉)"]),
    ("happy",    [r"\b(happy|great|amazing|love|awesome|good|nice|perfect|blessed)\b", r"(😊|😄|🥰|❤️)"]),
    ("lonely",   [r"\b(alone|lonely|no friends|nobody|nothing to do|by myself)\b"]),
    ("romantic", [r"\b(love you|crush|date|boyfriend|girlfriend|kiss|marry|feelings)\b", r"(❤️|💕|😍|🥰)"]),
    ("trolling", [r"\b(lmao|lmfao|bruh|ratio|skill issue|cope)\b", r"(💀|😂)"]),
    ("bored",    [r"\b(bored|nothing to do|idk|meh|whatever|bleh)\b", r"(😒|🥱|😑)"]),
    ("anxious",  [r"\b(anxious|nervous|scared|worried|stress|panic|overwhelmed)\b", r"(😰|😟|😬)"]),
]

_INSTRUCTIONS = {
    "angry":    "User seems angry. Acknowledge it. Be real, not dismissive.",
    "sad":      "User seems sad. Be present and genuine first, don't immediately try to fix things.",
    "excited":  "User is hyped. Match that energy.",
    "happy":    "User is in a good mood. Keep it positive.",
    "lonely":   "User might be lonely. Be warm and present.",
    "romantic": "User is in a romantic headspace. Be warm.",
    "trolling": "User is being playful. Give it back.",
    "bored":    "User is bored. Be more interesting than usual.",
    "anxious":  "User seems anxious. Be calm and grounding.",
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
