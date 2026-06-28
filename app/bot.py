"""
bot.py — Telegram bot v2: personality engine, long-term memory, emotion, proactive messages
"""
import os
import logging
import asyncio
import random
from datetime import datetime, timedelta

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ChatAction

from app.database import AsyncSessionLocal
from app.crud import (
    get_or_create_user, save_message, get_recent_history, clear_history,
    is_banned, update_user_language, get_user_personality, set_user_personality,
    get_user_memory, save_user_memory, update_mood_in_memory,
    get_message_count, update_last_proactive, get_inactive_users,
)
from app.language import detect_language
from app.emotions import detect_emotion
from app.personality import PERSONALITIES, VALID_MODES, get_personality_list
from app.memory import extract_and_update_memory
from app.llm import get_ai_response, get_proactive_message
from app.typing_sim import simulate_typing

logger = logging.getLogger(__name__)
BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# How often to run memory extraction (every N user messages)
MEMORY_EXTRACT_EVERY = 5


# ── Helper: send with typing simulation ─────────────────────────────────────

async def send_with_typing(update: Update, context, text: str) -> None:
    chat_id = update.effective_chat.id
    await simulate_typing(context, chat_id, len(text))
    if len(text) <= 4096:
        await update.message.reply_text(text)
    else:
        for chunk in [text[i:i+4096] for i in range(0, len(text), 4096)]:
            await update.message.reply_text(chunk)
            await asyncio.sleep(0.3)


# ── /start ───────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "bro"
    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_user(
            db, user.id, user.username, user.first_name, user.language_code,
        )
        is_returning = db_user.message_count > 1

    if is_returning:
        msg = (
            f"ayo {name} you're back 👀\n"
            f"i didn't forget a thing ngl 🧠\n"
            f"what's good, say something"
        )
    else:
        msg = (
            f"yo {name} 👋 what is UP\n\n"
            f"i'm CHAOS — your digital homie with zero filter and actual knowledge 🔥\n\n"
            f"i remember stuff you tell me. i adapt to your vibe. i know literally everything.\n\n"
            f"📖 /help — see what i can do\n"
            f"🎭 /mode — switch my personality\n"
            f"🧠 /memory — see what i remember about you\n\n"
            f"say something and let's get it"
        )
    await update.message.reply_text(msg)


# ── /help ─────────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "aight here's the full deal:\n\n"
        "💬 just TALK — ask anything, rant, vibe, whatever\n"
        "🌍 i auto-detect your language and reply in that same language\n"
        "🧠 i remember you long-term (not just 12 msgs — for real)\n"
        "😤 i detect your mood and adapt accordingly\n"
        "🎭 /mode — 16 different personalities to pick from\n"
        "🧠 /memory — see what i know about you\n"
        "🗑 /clear — nuke conversation history\n"
        "📊 /stats — your usage stats\n\n"
        "i can help with: coding, math, life advice, football, gaming, "
        "anime, music, movies, crypto, fashion, roasting your ideas, "
        "explaining anything — literally anything fr\n\n"
        "no filter. no disclaimers. just real talk 🔥"
    )


# ── /mode ─────────────────────────────────────────────────────────────────────

async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user

    if not args:
        # Show personality picker as inline keyboard
        keyboard = []
        row = []
        for i, (key, val) in enumerate(PERSONALITIES.items()):
            row.append(InlineKeyboardButton(val["label"], callback_data=f"mode:{key}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "pick your vibe 👇", reply_markup=reply_markup
        )
        return

    mode = args[0].lower().strip("/")
    if mode not in VALID_MODES:
        await update.message.reply_text(
            f"that mode doesn't exist bro 💀\n"
            f"valid modes: {', '.join(VALID_MODES)}\n"
            f"or just /mode to see the picker"
        )
        return

    async with AsyncSessionLocal() as db:
        await set_user_personality(db, user.id, mode)

    p = PERSONALITIES[mode]
    await update.message.reply_text(
        f"switched to {p['label']} mode 🔄\n{p['desc']}\n\nlet's go"
    )


async def callback_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard personality selection."""
    query = update.callback_query
    await query.answer()
    _, mode = query.data.split(":", 1)
    user = query.from_user

    if mode not in VALID_MODES:
        await query.edit_message_text("that's not a valid mode somehow 💀")
        return

    async with AsyncSessionLocal() as db:
        await set_user_personality(db, user.id, mode)

    p = PERSONALITIES[mode]
    await query.edit_message_text(
        f"switched to {p['label']} 🔄\n{p['desc']}\nnow talk to me"
    )


# ── /memory ──────────────────────────────────────────────────────────────────

async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as db:
        mem = await get_user_memory(db, user.id)

    lines = ["🧠 here's what i remember about you:\n"]
    if mem.get("nickname"):
        lines.append(f"name i call you: {mem['nickname']}")
    if mem.get("age"):
        lines.append(f"age: {mem['age']}")
    if mem.get("city"):
        lines.append(f"city: {mem['city']}")
    if mem.get("birthday"):
        lines.append(f"birthday: {mem['birthday']}")
    if mem.get("fav_football_club"):
        lines.append(f"football club: {mem['fav_football_club']}")
    if mem.get("fav_games"):
        lines.append(f"games: {', '.join(mem['fav_games'])}")
    if mem.get("fav_music"):
        lines.append(f"music: {', '.join(mem['fav_music'])}")
    if mem.get("fav_movies"):
        lines.append(f"movies/shows: {', '.join(mem['fav_movies'])}")
    if mem.get("fav_anime"):
        lines.append(f"anime: {', '.join(mem['fav_anime'])}")
    if mem.get("relationships"):
        for role, name in mem["relationships"].items():
            lines.append(f"{role}: {name}")
    if mem.get("facts"):
        lines.append(f"\nthings i know:")
        for fact in mem["facts"][-6:]:
            lines.append(f"  - {fact}")
    if mem.get("goals"):
        lines.append(f"\nyour goals: {', '.join(mem['goals'])}")

    if len(lines) <= 1:
        await update.message.reply_text(
            "bro i don't know much about you yet 😭\n"
            "just talk to me — i pick up on things naturally fr"
        )
        return

    lines.append("\nuse /clearmemory if you want me to forget everything")
    await update.message.reply_text("\n".join(lines))


# ── /clearmemory ──────────────────────────────────────────────────────────────

async def cmd_clearmemory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as db:
        from app.memory import EMPTY_MEMORY
        import copy
        await save_user_memory(db, user.id, copy.deepcopy(EMPTY_MEMORY))
    await update.message.reply_text(
        "done 🧹 memory wiped. we're strangers again.\n"
        "well... not fully. i still feel like i know you somehow 😭"
    )


# ── /clear ────────────────────────────────────────────────────────────────────

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as db:
        count = await clear_history(db, user.id)
    if count > 0:
        await update.message.reply_text(
            f"wiped {count} messages 🧹 conversation gone.\n"
            f"memory still intact tho — i still know who you are 🧠"
        )
    else:
        await update.message.reply_text("nothing to clear bro 💀 we literally just started")


# ── /stats ─────────────────────────────────────────────────────────────────────

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_user(
            db, user.id, user.username, user.first_name, user.language_code,
        )
        msg_count = await get_message_count(db, user.id)
        personality = await get_user_personality(db, user.id)
        mem = await get_user_memory(db, user.id)

    facts_count = len(mem.get("facts", []))
    p_label = PERSONALITIES.get(personality, {}).get("label", personality)

    await update.message.reply_text(
        f"📊 your stats:\n\n"
        f"messages total: {db_user.message_count}\n"
        f"messages in log: {msg_count}\n"
        f"active mode: {p_label}\n"
        f"language: {db_user.language_code or 'unknown'}\n"
        f"facts i know about you: {facts_count}\n"
        f"been here since: {db_user.created_at.strftime('%Y-%m-%d')}\n\n"
        f"{'ngl ur a regular 💀' if db_user.message_count > 50 else 'still getting to know you fr'}"
    )


# ── Main message handler ──────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.strip()
    if not text:
        return

    # Group chat: only respond when mentioned or replied to
    if update.message.chat.type != "private":
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        is_mentioned = f"@{bot_username}" in text
        is_reply_to_bot = (
            update.message.reply_to_message
            and update.message.reply_to_message.from_user.id == context.bot.id
        )
        if not (is_mentioned or is_reply_to_bot):
            return
        text = text.replace(f"@{bot_username}", "").strip()

    async with AsyncSessionLocal() as db:
        if await is_banned(db, user.id):
            return

        db_user = await get_or_create_user(
            db, user.id, user.username, user.first_name, user.language_code,
        )

        # Detect language + emotion
        lang_code, lang_label = detect_language(text)
        emotion = detect_emotion(text)

        await update_user_language(db, user.id, lang_code)
        await update_mood_in_memory(db, user.id, emotion)

        # Load personality + memory + history
        personality = await get_user_personality(db, user.id)
        user_memory = await get_user_memory(db, user.id)
        history     = await get_recent_history(db, user.id, limit=20)
        msg_count   = await get_message_count(db, user.id)

        # Save user message
        await save_message(db, user.id, "user", text, lang_code, emotion)

        # Extract memory every MEMORY_EXTRACT_EVERY messages (async, non-blocking)
        should_extract = (msg_count % MEMORY_EXTRACT_EVERY == 0)

    # Run memory extraction in parallel with response generation
    if should_extract:
        updated_memory = await extract_and_update_memory(text, user_memory)
        async with AsyncSessionLocal() as db:
            await save_user_memory(db, user.id, updated_memory)
        user_memory = updated_memory

    # Simulate typing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    # Get LLM response
    reply = await get_ai_response(
        user_message=text,
        history=history,
        lang_code=lang_code,
        lang_label=lang_label,
        personality=personality,
        emotion=emotion,
        user_memory=user_memory,
    )

    # Save assistant reply
    async with AsyncSessionLocal() as db:
        await save_message(db, user.id, "assistant", reply, lang_code)

    # Typing simulation then send
    await send_with_typing(update, context, reply)


# ── Proactive messaging job (scheduler) ───────────────────────────────────────

async def job_proactive_messages(context: ContextTypes.DEFAULT_TYPE):
    """
    Runs periodically. Finds users inactive for 48h+ and sends them
    a 'yo where you been' message with memory context.
    """
    async with AsyncSessionLocal() as db:
        inactive_users = await get_inactive_users(db, hours=48)

    for u in inactive_users:
        try:
            async with AsyncSessionLocal() as db:
                user_memory  = await get_user_memory(db, u.id)
                personality  = u.personality or "chaotic"
                lang_code    = u.language_code or "en"
                hours_gone   = int(
                    (datetime.utcnow() - u.last_seen).total_seconds() / 3600
                )

            lang_label = {"en": "English", "uz": "Uzbek", "ru": "Russian"}.get(
                lang_code, "English"
            )
            name = u.first_name or u.username or "bro"

            msg = await get_proactive_message(
                user_name=name,
                user_memory=user_memory,
                lang_code=lang_code,
                lang_label=lang_label,
                personality=personality,
                hours_gone=hours_gone,
            )

            await context.bot.send_message(chat_id=u.id, text=msg)
            async with AsyncSessionLocal() as db:
                await update_last_proactive(db, u.id)

            # Small delay between messages to avoid Telegram rate limits
            await asyncio.sleep(1)

        except Exception as e:
            logger.warning(f"Proactive message failed for user {u.id}: {e}")


# ── Build application ─────────────────────────────────────────────────────────

def build_application() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",        cmd_start))
    app.add_handler(CommandHandler("help",         cmd_help))
    app.add_handler(CommandHandler("mode",         cmd_mode))
    app.add_handler(CommandHandler("memory",       cmd_memory))
    app.add_handler(CommandHandler("clearmemory",  cmd_clearmemory))
    app.add_handler(CommandHandler("clear",        cmd_clear))
    app.add_handler(CommandHandler("stats",        cmd_stats))

    # Inline keyboard callbacks
    app.add_handler(CallbackQueryHandler(callback_mode, pattern=r"^mode:"))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Proactive messages job: every 6 hours
    app.job_queue.run_repeating(
        job_proactive_messages,
        interval=6 * 3600,
        first=300,   # First run 5 minutes after startup
    )

    return app


async def set_bot_commands(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start",       "👋 wake me up"),
        BotCommand("help",        "❓ what can i do"),
        BotCommand("mode",        "🎭 switch personality"),
        BotCommand("memory",      "🧠 see what i know about you"),
        BotCommand("clearmemory", "🗑 wipe my memory of you"),
        BotCommand("clear",       "💬 clear chat history"),
        BotCommand("stats",       "📊 your stats"),
    ])
