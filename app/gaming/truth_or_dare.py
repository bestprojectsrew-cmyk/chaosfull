"""gaming/truth_or_dare.py — Truth or Dare with AI-generated questions."""
import random
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

TRUTHS = [
    "What's the most embarrassing thing that happened to you this year?",
    "What's a secret you've never told anyone in this group?",
    "Who in this group do you think is the funniest?",
    "What's the worst lie you've ever told?",
    "What's something you're genuinely afraid of?",
]

DARES = [
    "Send the last photo in your camera roll right now",
    "Type a message using only your nose",
    "Speak in rhymes for the next 3 messages",
    "Write a poem about the person who sent the last message",
    "Change your profile photo to something weird for 10 minutes",
]


async def start_game(query, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["game_tod_started"] = True

    await query.edit_message_text(
        "🎯 Truth or Dare!\n\n"
        "How to play:\n"
        "• Type /join to join the game\n"
        "• Press Truth or Dare below\n"
        "• Bot picks a random question/dare for you\n\n"
        "First, everyone /join!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤔 Truth",  callback_data="tod:truth"),
             InlineKeyboardButton("😈 Dare",   callback_data="tod:dare")],
            [InlineKeyboardButton("🛑 Stop game", callback_data="game:stop")],
        ]),
    )


async def cb_tod(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data.split(":", 1)[1]

    name = query.from_user.first_name or "you"

    if choice == "truth":
        question = random.choice(TRUTHS)
        await query.message.reply_text(
            f"🤔 Truth for {name}:\n\n{question}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤔 Truth",  callback_data="tod:truth"),
                 InlineKeyboardButton("😈 Dare",   callback_data="tod:dare")],
                [InlineKeyboardButton("🛑 Stop game", callback_data="game:stop")],
            ])
        )
    elif choice == "dare":
        dare = random.choice(DARES)
        await query.message.reply_text(
            f"😈 Dare for {name}:\n\n{dare}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤔 Truth",  callback_data="tod:truth"),
                 InlineKeyboardButton("😈 Dare",   callback_data="tod:dare")],
                [InlineKeyboardButton("🛑 Stop game", callback_data="game:stop")],
            ])
        )
