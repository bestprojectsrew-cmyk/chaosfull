"""gaming/would_you_rather.py — Would You Rather with voting."""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

WYR_QUESTIONS = [
    ("Have no internet for a week", "No food for 3 days"),
    ("Always speak in rhymes", "Always speak in reverse"),
    ("Be the funniest person alive", "Be the smartest person alive"),
    ("Know when you'll die", "Know how you'll die"),
    ("Have unlimited money but no friends", "Have unlimited friends but no money"),
    ("Live in 1800s", "Live in 2200s"),
    ("Never use social media again", "Never watch movies/shows again"),
    ("Win a World Cup", "Win an Oscar"),
    ("Be famous and broke", "Be rich and unknown"),
    ("Only eat your favorite food forever", "Never eat it again"),
]


async def start_game(query, context: ContextTypes.DEFAULT_TYPE):
    import random
    questions = WYR_QUESTIONS.copy()
    random.shuffle(questions)
    context.chat_data["game_wyr_questions"] = questions
    context.chat_data["game_wyr_qindex"] = 0
    context.chat_data["game_wyr_votes"] = {}

    a, b = questions[0]
    context.chat_data["game_wyr_current"] = (a, b)

    await query.edit_message_text(
        f"🎭 Would You Rather!\n\nQuestion 1:\n\nWould you rather...\n\nA) {a}\n\nor\n\nB) {b}\n\nVote below! 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"A: {a[:30]}", callback_data="wyr:a"),
             InlineKeyboardButton(f"B: {b[:30]}", callback_data="wyr:b")],
            [InlineKeyboardButton("⏭ Next question", callback_data="wyr:next"),
             InlineKeyboardButton("🛑 Stop",          callback_data="game:stop")],
        ]),
    )


async def cb_wyr(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.split(":", 1)[1]
    user = query.from_user
    name = user.first_name or "someone"

    if action in ("a", "b"):
        votes = context.chat_data.get("game_wyr_votes", {})
        votes[user.id] = action
        context.chat_data["game_wyr_votes"] = votes

        a_votes = sum(1 for v in votes.values() if v == "a")
        b_votes = sum(1 for v in votes.values() if v == "b")
        current = context.chat_data.get("game_wyr_current", ("A", "B"))

        await query.answer(f"You voted {action.upper()}!", show_alert=False)

        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"A ({a_votes}✓)", callback_data="wyr:a"),
                     InlineKeyboardButton(f"B ({b_votes}✓)", callback_data="wyr:b")],
                    [InlineKeyboardButton("⏭ Next question", callback_data="wyr:next"),
                     InlineKeyboardButton("🛑 Stop",          callback_data="game:stop")],
                ])
            )
        except Exception:
            pass

    elif action == "next":
        import random
        questions = context.chat_data.get("game_wyr_questions", [])
        qindex = context.chat_data.get("game_wyr_qindex", 0) + 1

        if qindex >= len(questions):
            from app.gaming.game_manager import stop_game
            stop_game(context.chat_data)
            await query.edit_message_text("🎭 That's all the questions! /game to play again")
            return

        context.chat_data["game_wyr_qindex"] = qindex
        context.chat_data["game_wyr_votes"] = {}
        a, b = questions[qindex]
        context.chat_data["game_wyr_current"] = (a, b)

        await query.edit_message_text(
            f"🎭 Question {qindex + 1}:\n\nWould you rather...\n\nA) {a}\n\nor\n\nB) {b}\n\nVote! 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"A: {a[:30]}", callback_data="wyr:a"),
                 InlineKeyboardButton(f"B: {b[:30]}", callback_data="wyr:b")],
                [InlineKeyboardButton("⏭ Next question", callback_data="wyr:next"),
                 InlineKeyboardButton("🛑 Stop",          callback_data="game:stop")],
            ]),
        )
