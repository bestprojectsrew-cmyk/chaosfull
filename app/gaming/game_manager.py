"""
gaming/game_manager.py — Central game state controller.

Only ONE game active per group at a time.
All games register here. Game manager handles:
  - Starting / stopping games
  - Player join/leave
  - Turn management
  - Auto-timeout
  - State persistence in chat_data (survives bot restarts via PTB)

Commands handled here:
  /game    — show game picker
  /join    — join current game
  /leave   — leave current game
  /players — list current players
  /stopgame — stop active game (admins only)
"""

import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

GAME_TIMEOUT = 30  # seconds per turn before auto-skip


def get_active_game(chat_data: dict) -> str | None:
    return chat_data.get("active_game")


def get_players(chat_data: dict) -> list[dict]:
    return chat_data.get("game_players", [])


def add_player(chat_data: dict, user_id: int, name: str) -> bool:
    players = chat_data.setdefault("game_players", [])
    if any(p["id"] == user_id for p in players):
        return False
    players.append({"id": user_id, "name": name})
    return True


def remove_player(chat_data: dict, user_id: int) -> bool:
    players = chat_data.get("game_players", [])
    before = len(players)
    chat_data["game_players"] = [p for p in players if p["id"] != user_id]
    return len(chat_data["game_players"]) < before


def stop_game(chat_data: dict) -> str | None:
    game = chat_data.pop("active_game", None)
    chat_data.pop("game_players", None)
    chat_data.pop("game_state", None)
    chat_data.pop("game_turn_index", None)
    # Clear individual game states
    for key in list(chat_data.keys()):
        if key.startswith("game_"):
            chat_data.pop(key, None)
    return game


def _game_keyboard(active: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🎯 Truth or Dare",   callback_data="game:tod")],
        [InlineKeyboardButton("❓ Trivia Battle",    callback_data="game:trivia")],
        [InlineKeyboardButton("🔢 Number Guess",     callback_data="game:numguess")],
        [InlineKeyboardButton("🎭 Would You Rather", callback_data="game:wyr")],
        [InlineKeyboardButton("🔤 Word Chain",       callback_data="game:wordchain")],
    ]
    if active:
        rows.append([InlineKeyboardButton(f"🛑 Stop {active}", callback_data="game:stop")])
    return InlineKeyboardMarkup(rows)


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = get_active_game(context.chat_data)
    players = get_players(context.chat_data)

    if active:
        player_list = ", ".join(p["name"] for p in players) if players else "no one yet"
        await update.message.reply_text(
            f"⚠️ {active} is running right now\n"
            f"Players: {player_list}\n\n"
            f"Press stop to end it, or pick a new game to replace it:",
            reply_markup=_game_keyboard(active),
        )
    else:
        await update.message.reply_text(
            "🎮 Pick a game:\n\n"
            "Truth or Dare — bot asks each person\n"
            "Trivia Battle — answer fastest wins\n"
            "Number Guess — 1 to 100\n"
            "Would You Rather — group votes\n"
            "Word Chain — continue from last letter",
            reply_markup=_game_keyboard(),
        )


async def cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = get_active_game(context.chat_data)
    if not active:
        await update.message.reply_text("no game running. use /game to start one")
        return

    user = update.effective_user
    name = user.first_name or user.username or "Unknown"
    joined = add_player(context.chat_data, user.id, name)
    players = get_players(context.chat_data)

    if joined:
        await update.message.reply_text(
            f"✅ {name} joined! {len(players)} player{'s' if len(players) != 1 else ''} so far"
        )
    else:
        await update.message.reply_text(f"you're already in {active} 👀")


async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = get_active_game(context.chat_data)
    if not active:
        await update.message.reply_text("no game running")
        return

    user = update.effective_user
    left = remove_player(context.chat_data, user.id)
    name = user.first_name or user.username or "Unknown"

    if left:
        players = get_players(context.chat_data)
        await update.message.reply_text(f"👋 {name} left. {len(players)} players remaining")
        if len(players) == 0:
            stop_game(context.chat_data)
            await update.message.reply_text("no players left — game ended")
    else:
        await update.message.reply_text("you weren't in the game")


async def cmd_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active = get_active_game(context.chat_data)
    if not active:
        await update.message.reply_text("no game running")
        return

    players = get_players(context.chat_data)
    if not players:
        await update.message.reply_text(f"{active} has no players yet. use /join")
        return

    names = "\n".join(f"{i+1}. {p['name']}" for i, p in enumerate(players))
    await update.message.reply_text(f"👥 Players in {active}:\n\n{names}")


async def cmd_stopgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check admin
    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        is_admin = member.status in ("administrator", "creator")
    except Exception:
        is_admin = False

    active = get_active_game(context.chat_data)
    if not active:
        await update.message.reply_text("no game is running")
        return

    if not is_admin:
        await update.message.reply_text("only admins can stop games")
        return

    stop_game(context.chat_data)
    await update.message.reply_text(f"🛑 {active} stopped\n\nuse /game to start a new one")


async def cb_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle game selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    game_id = query.data.split(":", 1)[1]

    if game_id == "stop":
        active = get_active_game(context.chat_data)
        stopped = stop_game(context.chat_data)
        if stopped:
            await query.edit_message_text(
                f"🛑 {stopped} stopped\n\nuse /game to start a new one"
            )
        else:
            await query.edit_message_text("no game was running")
        return

    # Stop current game if switching
    current = get_active_game(context.chat_data)
    if current and current != game_id:
        stop_game(context.chat_data)

    # Route to individual game starters
    from app.gaming import number_guess, word_chain, trivia, truth_or_dare, would_you_rather

    game_starters = {
        "numguess":  number_guess.start_game,
        "wordchain": word_chain.start_game,
        "trivia":    trivia.start_game,
        "tod":       truth_or_dare.start_game,
        "wyr":       would_you_rather.start_game,
    }

    starter = game_starters.get(game_id)
    if starter:
        context.chat_data["active_game"] = game_id
        context.chat_data["game_players"] = []
        await starter(query, context)
    else:
        await query.edit_message_text("unknown game")
