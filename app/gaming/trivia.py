"""gaming/trivia.py — Trivia battle with scoreboard."""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

TRIVIA_QUESTIONS = [
    ("How many players are in a football team?", "11"),
    ("What country has won the most FIFA World Cups?", "brazil"),
    ("What is the capital of Japan?", "tokyo"),
    ("How many sides does a hexagon have?", "6"),
    ("What planet is closest to the Sun?", "mercury"),
    ("What year did World War 2 end?", "1945"),
    ("Who painted the Mona Lisa?", "da vinci"),
    ("What is the largest ocean on Earth?", "pacific"),
    ("How many continents are there?", "7"),
    ("What is the chemical symbol for water?", "h2o"),
]


async def start_game(query, context: ContextTypes.DEFAULT_TYPE):
    import random
    questions = TRIVIA_QUESTIONS.copy()
    random.shuffle(questions)
    context.chat_data["game_trivia_questions"] = questions
    context.chat_data["game_trivia_scores"] = {}
    context.chat_data["game_trivia_qindex"] = 0

    q, _ = questions[0]
    await query.edit_message_text(
        f"❓ Trivia Battle!\n\nFirst to answer correctly wins the point!\n\n"
        f"Question 1:\n{q}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🛑 Stop game", callback_data="game:stop")],
             [InlineKeyboardButton("⏭ Skip question", callback_data="game:trivia_skip")]]
        ),
    )


async def handle_answer(update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    questions = context.chat_data.get("game_trivia_questions")
    if not questions:
        return False

    qindex = context.chat_data.get("game_trivia_qindex", 0)
    if qindex >= len(questions):
        return False

    _, answer = questions[qindex]
    text = update.message.text.strip().lower()

    if answer.lower() not in text:
        return False

    # Correct!
    user = update.effective_user
    name = user.first_name or user.username or "someone"
    scores = context.chat_data.get("game_trivia_scores", {})
    scores[name] = scores.get(name, 0) + 1
    context.chat_data["game_trivia_scores"] = scores

    next_index = qindex + 1
    context.chat_data["game_trivia_qindex"] = next_index

    scoreboard = " | ".join(f"{n}: {s}" for n, s in sorted(scores.items(), key=lambda x: -x[1]))

    if next_index >= len(questions):
        # Game over
        from app.gaming.game_manager import stop_game
        stop_game(context.chat_data)
        winner = max(scores, key=scores.get)
        await update.message.reply_text(
            f"🎉 {name} got it! The answer was '{answer}'\n\n"
            f"🏆 Game over!\n{scoreboard}\n\nWinner: {winner} 🥇\n\n/game to play again"
        )
    else:
        next_q, _ = questions[next_index]
        await update.message.reply_text(
            f"✅ {name} got it! +1 point\n\nScores: {scoreboard}\n\n"
            f"Question {next_index + 1}:\n{next_q}"
        )

    return True
