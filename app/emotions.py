"""
emotions.py — Detect user emotional state from message content
"""
import re

# Keyword sets per emotion — order matters (checked top to bottom)
EMOTION_PATTERNS = [
    ("angry", [
        r"\b(fuck|wtf|pissed|mad|angry|furious|rage|hate|shut up|idiot|stupid|dumb|kill)\b",
        r"[!]{3,}",
        r"(ugh+|argh+|grrr+)",
    ]),
    ("sad", [
        r"\b(sad|depressed|cry|crying|lonely|alone|miss|hurt|broken|lost|empty|hopeless|tired of)\b",
        r"(😢|😭|💔|🥺|😞|😔)",
        r"\b(nobody cares|no one|can't anymore|give up)\b",
    ]),
    ("excited", [
        r"\b(omg|omfg|yesss|let's go|lets go|woah|wow|insane|crazy|fire|lit|🔥|hype|finally)\b",
        r"[!]{2,}",
        r"(!!!|😱|🤩|🔥|💥|🎉)",
    ]),
    ("happy", [
        r"\b(happy|great|amazing|love|awesome|good|nice|perfect|blessed|grateful|winning)\b",
        r"(😊|😄|🥰|❤️|💕|✨|😁)",
    ]),
    ("lonely", [
        r"\b(alone|lonely|no friends|nobody|bored|nothing to do|just me|by myself)\b",
        r"\b(talking to an ai|you're my only|no one talks)\b",
    ]),
    ("romantic", [
        r"\b(love you|crush|date|boyfriend|girlfriend|kiss|marry|together|feelings|relationship)\b",
        r"(❤️|💕|😍|🥰|💗|💘|💓)",
    ]),
    ("trolling", [
        r"\b(lmao|lmfao|💀|😂|haha|bruh|lol|ratio|L \+|skill issue|cope)\b",
        r"(kekw|pog|pepega|monka)",
    ]),
    ("bored", [
        r"\b(bored|nothing to do|idk|meh|whatever|don't care|who cares|bleh|zzz)\b",
        r"(😒|🥱|😑|😐)",
    ]),
    ("anxious", [
        r"\b(anxious|nervous|scared|worried|stress|panic|overwhelmed|can't sleep|what if)\b",
        r"(😰|😟|😬|😨)",
    ]),
]

# How to adapt tone per detected emotion
EMOTION_INSTRUCTIONS = {
    "angry": (
        "The user seems ANGRY or frustrated. Match their energy a little — don't be dismissive. "
        "Acknowledge what they're upset about. Be real, not fake-calm. "
        "Help if you can, vent with them if that's what they need."
    ),
    "sad": (
        "The user seems SAD or down. Shift to a softer, more present tone. "
        "Don't immediately try to fix things. First just be there. "
        "Say something real, not a motivational poster. Check in on them."
    ),
    "excited": (
        "The user is HYPED or excited. MATCH THAT ENERGY. Go off with them. "
        "React big. Be their hype person fr fr. Amplify the good vibes."
    ),
    "happy": (
        "The user is in a good mood. Keep the positive energy going. "
        "Be fun, light, match their happiness. Celebrate with them if relevant."
    ),
    "lonely": (
        "The user might be feeling lonely. Be extra warm and present. "
        "Make them feel heard and seen. Don't rush the conversation. "
        "Be the homie they needed rn."
    ),
    "romantic": (
        "The user is in a romantic headspace. Be warm, maybe a bit more personal. "
        "Don't be weird about it — just be real and kind."
    ),
    "trolling": (
        "The user is being playful / trolling. Match that chaotic energy. "
        "Give it back to them. Be funny. Don't take anything too seriously rn."
    ),
    "bored": (
        "The user is bored. Be more entertaining than usual. "
        "Say something interesting, funny, or unexpected to shake them out of it."
    ),
    "anxious": (
        "The user seems anxious or worried. Be grounding and calm. "
        "Acknowledge the feeling first. Then help them think through it step by step."
    ),
    "neutral": "",
}


def detect_emotion(text: str) -> str:
    """Returns the detected emotion label from the message text."""
    text_lower = text.lower()
    for emotion, patterns in EMOTION_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return emotion
    return "neutral"


def get_emotion_instruction(emotion: str) -> str:
    return EMOTION_INSTRUCTIONS.get(emotion, "")
