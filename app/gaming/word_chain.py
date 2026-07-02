"""gaming/word_chain.py — Word chain game with proper turns and timeout."""
import asyncio
import logging
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


async def start_game(query, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["game_wordchain_current"] = "chaos"
    context.chat_data["game_wordchain_used"] = {"chaos"}
    context.chat_data["game_wordchain_started"] = True

    await query.edit_message_text(
        "🔤 Word Chain!\n\n"
        "Rules:\n"
        "• Each word must start with the LAST letter of the previous word\n"
        "• No repeated words\n"
        "• Single words only\n\n"
        "First word: CHAOS\n"
        "Next word must start with: S 👇",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🛑 Stop game", callback_data="game:stop")]]
        ),
    )


async def handle_word(update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Returns True if message was a valid word chain move."""
    if not context.chat_data.get("game_wordchain_started"):
        return False

    text = update.message.text.strip().lower()
    words = text.split()

    # Only handle single words
    if len(words) != 1 or not words[0].isalpha():
        return False

    word = words[0]
    current = context.chat_data.get("game_wordchain_current", "")
    used = context.chat_data.get("game_wordchain_used", set())
    name = update.effective_user.first_name or "you"

    if not current:
        return False

    if word in used:
        await update.message.reply_text(f"❌ '{word}' was already used 💀")
        return True

    if word[0] != current[-1]:
        await update.message.reply_text(
            f"❌ must start with '{current[-1].upper()}', not '{word[0].upper()}'"
        )
        return True

    # Valid
    context.chat_data["game_wordchain_current"] = word
    used.add(word)
    context.chat_data["game_wordchain_used"] = used

    await update.message.reply_text(
        f"✅ {name}: {word}\nnext must start with '{word[-1].upper()}' 👇"
    )
    return True
