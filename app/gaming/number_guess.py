"""gaming/number_guess.py — Number guessing game."""
import random
import logging
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

STOP_BUTTON = [["🛑 Stop game", "game:stop"]]


async def start_game(query, context: ContextTypes.DEFAULT_TYPE):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    secret = random.randint(1, 100)
    context.chat_data["game_numguess_secret"] = secret
    context.chat_data["game_numguess_guesses"] = 0

    await query.edit_message_text(
        "🔢 Number Guess!\n\n"
        "I'm thinking of a number between 1 and 100.\n"
        "First correct answer wins 🏆\n\n"
        "Start guessing 👇",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🛑 Stop game", callback_data="game:stop")]]
        ),
    )


async def handle_guess(update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Returns True if message was a valid guess."""
    from app.gaming.game_manager import stop_game

    text = update.message.text.strip()
    try:
        guess = int(text)
    except ValueError:
        return False

    secret = context.chat_data.get("game_numguess_secret")
    if secret is None:
        return False

    context.chat_data["game_numguess_guesses"] = context.chat_data.get("game_numguess_guesses", 0) + 1
    guesses = context.chat_data["game_numguess_guesses"]
    name = update.effective_user.first_name or "you"

    if guess == secret:
        stop_game(context.chat_data)
        await update.message.reply_text(
            f"🎉 {name} got it in {guesses} guess{'es' if guesses != 1 else ''}!\n"
            f"The number was {secret} 🔥\n\n/game to play again"
        )
        return True
    elif guess < secret:
        await update.message.reply_text("📈 higher")
        return True
    else:
        await update.message.reply_text("📉 lower")
        return True
