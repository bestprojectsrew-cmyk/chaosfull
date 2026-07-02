"""
bot.py — Telegram bot: all handlers, commands, proactive messages.
"""
import os
import asyncio
import logging
from datetime import datetime

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
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
from app.personality import PERSONALITIES, VALID_MODES
from app.memory import extract_and_update_memory
from app.llm import get_ai_response, get_proactive_message
from app.group_handler import (
    should_jump_in, add_to_group_context, get_group_context,
    build_group_system_addition, _mark_replied,
)
from app.group_commands import (
    cmd_ban,
    cmd_unban,
    cmd_kick,
    cmd_mute,
    cmd_unmute,
    cmd_warn,
    cmd_warns,
    cmd_pin,
    cmd_promote,
    cmd_demote,
    cmd_purge,
    cmd_id,
    cmd_userinfo,
    cmd_chatinfo,
    cmd_couple,
    cmd_game,
    cb_game,
    handle_game_messages,
)
from app.typing_sim import simulate_typing

logger = logging.getLogger(__name__)

BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
MEMORY_EXTRACT_EVERY = 5   # run memory extraction every N messages


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _send(update: Update, context, text: str) -> None:
    """Send reply with typing simulation."""
    await simulate_typing(context, update.effective_chat.id, len(text))
    if len(text) <= 4096:
        await update.message.reply_text(text)
    else:
        for chunk in [text[i:i+4096] for i in range(0, len(text), 4096)]:
            await update.message.reply_text(chunk)
            await asyncio.sleep(0.2)


# ── /start ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"
    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_user(
            db, user.id, user.username, user.first_name, user.language_code,
        )
    if db_user.message_count > 1:
        await update.message.reply_text(f"{name}, you're back. what's good")
    else:
        await update.message.reply_text(
            f"hey {name} 👋\n\n"
            f"i'm Chaos — your AI friend. no filter, actual knowledge, real talk.\n\n"
            f"i remember stuff, adapt to your vibe, and search the web when needed.\n\n"
            f"/help — what i can do\n"
            f"/mode — switch personality\n"
            f"/memory — what i know about you\n\n"
            f"say something"
        )


# ── /help ─────────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "what i do:\n\n"
        "talk to me about anything — i search the web for current stuff automatically\n"
        "i detect your language and reply in it\n"
        "i remember things you tell me across conversations\n"
        "i detect your mood and adapt\n\n"
        "/mode — 16 personalities\n"
        "/memory — see what i remember\n"
        "/clearmemory — wipe my memory of you\n"
        "/clear — clear conversation history\n"
        "/stats — your stats\n\n"
        "coding, math, football, crypto, advice, roasting your ideas — whatever"
    )


# ── /mode ─────────────────────────────────────────────────────────────────────

async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if args:
        mode = args[0].lower().strip("/")
        if mode not in VALID_MODES:
            await update.message.reply_text(
                f"that mode doesn't exist. valid: {', '.join(VALID_MODES)}\nor /mode to see the picker"
            )
            return
        async with AsyncSessionLocal() as db:
            await set_user_personality(db, user.id, mode)
        p = PERSONALITIES[mode]
        await update.message.reply_text(f"switched to {p['label']} — {p['desc']}")
        return

    # Inline keyboard picker
    buttons, row = [], []
    for i, (key, val) in enumerate(PERSONALITIES.items()):
        row.append(InlineKeyboardButton(val["label"], callback_data=f"mode:{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await update.message.reply_text("pick a vibe 👇", reply_markup=InlineKeyboardMarkup(buttons))


async def cb_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split(":", 1)[1]
    if mode not in VALID_MODES:
        await query.edit_message_text("invalid mode")
        return
    async with AsyncSessionLocal() as db:
        await set_user_personality(db, query.from_user.id, mode)
    p = PERSONALITIES[mode]
    await query.edit_message_text(f"switched to {p['label']} — {p['desc']}")


# ── /memory ───────────────────────────────────────────────────────────────────

async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncSessionLocal() as db:
        mem = await get_user_memory(db, update.effective_user.id)

    lines = ["what i know about you:\n"]
    if mem.get("nickname"):   lines.append(f"you go by: {mem['nickname']}")
    if mem.get("age"):        lines.append(f"age: {mem['age']}")
    if mem.get("city"):       lines.append(f"city: {mem['city']}")
    if mem.get("birthday"):   lines.append(f"birthday: {mem['birthday']}")
    if mem.get("fav_football_club"): lines.append(f"football club: {mem['fav_football_club']}")
    if mem.get("fav_games"):  lines.append(f"games: {', '.join(mem['fav_games'])}")
    if mem.get("fav_music"):  lines.append(f"music: {', '.join(mem['fav_music'])}")
    if mem.get("fav_movies"): lines.append(f"shows/movies: {', '.join(mem['fav_movies'])}")
    if mem.get("fav_anime"):  lines.append(f"anime: {', '.join(mem['fav_anime'])}")
    if mem.get("job_or_school"): lines.append(f"work/school: {mem['job_or_school']}")
    if mem.get("relationships"):
        for role, name in list(mem["relationships"].items())[:5]:
            lines.append(f"{role}: {name}")
    if mem.get("facts"):
        lines.append("\nother things:")
        for f in mem["facts"][-6:]:
            lines.append(f"  {f}")
    if mem.get("goals"):
        lines.append(f"goals: {', '.join(mem['goals'])}")

    if len(lines) <= 1:
        await update.message.reply_text("i don't know much about you yet. just talk to me, i pick things up naturally")
        return
    lines.append("\n/clearmemory to wipe this")
    await update.message.reply_text("\n".join(lines))


# ── /clearmemory ──────────────────────────────────────────────────────────────

async def cmd_clearmemory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import copy
    from app.memory import EMPTY_MEMORY
    async with AsyncSessionLocal() as db:
        await save_user_memory(db, update.effective_user.id, copy.deepcopy(EMPTY_MEMORY))
    await update.message.reply_text("done, memory wiped. fresh start")


# ── /clear ────────────────────────────────────────────────────────────────────

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncSessionLocal() as db:
        count = await clear_history(db, update.effective_user.id)
    await update.message.reply_text(
        f"cleared {count} messages. memory still intact though" if count > 0
        else "nothing to clear"
    )


# ── /stats ────────────────────────────────────────────────────────────────────

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_user(db, user.id, user.username, user.first_name, user.language_code)
        msg_count = await get_message_count(db, user.id)
        personality = await get_user_personality(db, user.id)
        mem = await get_user_memory(db, user.id)

    p_label = PERSONALITIES.get(personality, {}).get("label", personality)
    await update.message.reply_text(
        f"your stats\n\n"
        f"messages sent: {db_user.message_count}\n"
        f"in conversation log: {msg_count}\n"
        f"active mode: {p_label}\n"
        f"language: {db_user.language_code or 'detecting'}\n"
        f"facts i know: {len(mem.get('facts', []))}\n"
        f"here since: {db_user.created_at.strftime('%Y-%m-%d')}"
    )


# ── Main message handler ──────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.strip()
    if not text:
        return

    # ── Group chat handling ──────────────────────────────────────────────────
    is_group = update.message.chat.type in ("group", "supergroup")

    # Check hashtag notes first (#notename shortcut)
    if is_group and update.message.text and update.message.text.startswith("#"):
        if await handle_hashtag_note(update, context):
            return

    # Check word filters
    if is_group:
        if await handle_filter_trigger(update, context):
            return

    # Check active games
    if is_group:
        from app.gaming import number_guess, word_chain, trivia
        active = context.chat_data.get("active_game")
        if active == "numguess":
            if await number_guess.handle_guess(update, context):
                return
        elif active == "wordchain":
            if await word_chain.handle_word(update, context):
                return
        elif active == "trivia":
            if await trivia.handle_answer(update, context):
                return
    group_context_block = ""
    jump_reason = "private"

    if is_group:
        # Ignore messages from other bots
        if user.is_bot:
            return

        bot_info = await context.bot.get_me()
        mention     = f"@{bot_info.username}"
        is_mention  = mention in text
        is_reply    = (
            update.message.reply_to_message is not None
            and update.message.reply_to_message.from_user is not None
            and update.message.reply_to_message.from_user.id == context.bot.id
        )

        # Store this message in group context buffer regardless
        sender_name = user.first_name or user.username or "someone"
        add_to_group_context(update.effective_chat.id, sender_name, text)

        # Decide whether to respond (includes name trigger like "chaoz" / "chaos")
        is_name_call = is_name_trigger(text)
        respond, jump_reason = should_jump_in(
            text, update.effective_chat.id, is_mention or is_name_call, is_reply
        )
        if not respond:
            return

        # Clean mention from text
        text = text.replace(mention, "").strip()

        # Build group context for LLM
        group_ctx   = get_group_context(update.effective_chat.id)
        group_name  = update.effective_chat.title or "the group"
        group_context_block = build_group_system_addition(group_ctx, group_name, jump_reason)
        _mark_replied(update.effective_chat.id)

    async with AsyncSessionLocal() as db:
        if await is_banned(db, user.id):
            return

        db_user = await get_or_create_user(
            db, user.id, user.username, user.first_name, user.language_code,
        )

        # Detect language from this specific message
        lang_code, lang_label = detect_language(text)
        emotion = detect_emotion(text)

        await update_user_language(db, user.id, lang_code)
        await update_mood_in_memory(db, user.id, emotion)

        personality = await get_user_personality(db, user.id)
        user_memory = await get_user_memory(db, user.id)
        history     = await get_recent_history(db, user.id, limit=MAX_HISTORY_DB)
        msg_count   = await get_message_count(db, user.id)

        await save_message(db, user.id, "user", text, lang_code, emotion)

    # Memory extraction every N messages (non-blocking to response speed)
    updated_memory = user_memory
    if msg_count % MEMORY_EXTRACT_EVERY == 0:
        updated_memory = await extract_and_update_memory(text, user_memory)
        async with AsyncSessionLocal() as db:
            await save_user_memory(db, user.id, updated_memory)

    # Typing simulation
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    # Generate response
    reply = await get_ai_response(
        user_message=text,
        history=history,
        lang_code=lang_code,
        lang_label=lang_label,
        personality=personality,
        emotion=emotion,
        user_memory=updated_memory,
        group_context_block=group_context_block,
    )

    # Save and send
    async with AsyncSessionLocal() as db:
        await save_message(db, user.id, "assistant", reply, lang_code)

    await _send(update, context, reply)


MAX_HISTORY_DB = 16


# ── Proactive messaging ───────────────────────────────────────────────────────

async def job_proactive(context: ContextTypes.DEFAULT_TYPE):
    """Check every 6h for users inactive 48h+ and send a check-in."""
    async with AsyncSessionLocal() as db:
        users = await get_inactive_users(db, hours=48)

    for u in users:
        try:
            async with AsyncSessionLocal() as db:
                mem  = await get_user_memory(db, u.id)
            hours_gone = int((datetime.utcnow() - u.last_seen).total_seconds() / 3600)
            lang_labels = {"uz": "Uzbek", "ru": "Russian", "tr": "Turkish", "ar": "Arabic"}
            lang_label  = lang_labels.get(u.language_code or "en", "English")
            name = u.first_name or u.username or "there"
            msg = await get_proactive_message(
                user_name=name, user_memory=mem,
                lang_code=u.language_code or "en", lang_label=lang_label,
                personality=u.personality or "chaotic", hours_gone=hours_gone,
            )
            await context.bot.send_message(chat_id=u.id, text=msg)
            async with AsyncSessionLocal() as db:
                await update_last_proactive(db, u.id)
            await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Proactive msg failed for {u.id}: {e}")


# ── Application builder ───────────────────────────────────────────────────────

def build_application() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",       cmd_start))
    app.add_handler(CommandHandler("help",        cmd_help))
    app.add_handler(CommandHandler("mode",        cmd_mode))
    app.add_handler(CommandHandler("memory",      cmd_memory))
    app.add_handler(CommandHandler("clearmemory", cmd_clearmemory))
    app.add_handler(CommandHandler("clear",       cmd_clear))
    app.add_handler(CommandHandler("stats",       cmd_stats))
    app.add_handler(CallbackQueryHandler(cb_mode, pattern=r"^mode:"))

    # ── Private chat only ─────────────────────────────────────────────────────
    private_filter = filters.ChatType.PRIVATE
    # app.add_handler(CommandHandler("panel", cmd_panel, filters=private_filter))
    # app.add_handler(CallbackQueryHandler(cb_panel, pattern=r"^panel:"))

    # ── Group-only commands ────────────────────────────────────────────────────
    group_filter = filters.ChatType.GROUPS

    # Admin moderation
    app.add_handler(CommandHandler("ban",       cmd_ban,       filters=group_filter))
    app.add_handler(CommandHandler("unban",     cmd_unban,     filters=group_filter))
    app.add_handler(CommandHandler("kick",      cmd_kick,      filters=group_filter))
    app.add_handler(CommandHandler("mute",      cmd_mute,      filters=group_filter))
    app.add_handler(CommandHandler("unmute",    cmd_unmute,    filters=group_filter))
    app.add_handler(CommandHandler("warn",      cmd_warn,      filters=group_filter))
    app.add_handler(CommandHandler("warns",     cmd_warns,     filters=group_filter))
    app.add_handler(CommandHandler("pin",       cmd_pin,       filters=group_filter))
    app.add_handler(CommandHandler("promote",   cmd_promote,   filters=group_filter))
    app.add_handler(CommandHandler("demote",    cmd_demote,    filters=group_filter))
    app.add_handler(CommandHandler("purge",     cmd_purge,     filters=group_filter))
    # app.add_handler(CommandHandler("lock",      cmd_lock,      filters=group_filter))
    # app.add_handler(CommandHandler("unlock",    cmd_unlock,    filters=group_filter))
    # app.add_handler(CommandHandler("slowmode",  cmd_slowmode,  filters=group_filter))
    app.add_handler(CommandHandler("id",        cmd_id,        filters=group_filter))
    app.add_handler(CommandHandler("userinfo",  cmd_userinfo,  filters=group_filter))
    app.add_handler(CommandHandler("chatinfo",  cmd_chatinfo,  filters=group_filter))

    # Filters + notes
    # app.add_handler(CommandHandler("filter",    cmd_filter,    filters=group_filter))
    # app.add_handler(CommandHandler("delfilter", cmd_delfilter, filters=group_filter))
    # app.add_handler(CommandHandler("filters",   cmd_filters,   filters=group_filter))
    # app.add_handler(CommandHandler("savenote",  cmd_savenote,  filters=group_filter))
    # app.add_handler(CommandHandler("getnote",   cmd_getnote,   filters=group_filter))
    # app.add_handler(CommandHandler("delnote",   cmd_delnote,   filters=group_filter))
    # app.add_handler(CommandHandler("notes",     cmd_notes,     filters=group_filter))

    # Fun group commands (visible in group menu)
    app.add_handler(CommandHandler("couple",    cmd_couple,    filters=group_filter))
    app.add_handler(CommandHandler("game",      cmd_game,      filters=group_filter))
    app.add_handler(CommandHandler("join",      cmd_join,      filters=group_filter))
    app.add_handler(CommandHandler("leave",     cmd_leave,     filters=group_filter))
    app.add_handler(CommandHandler("players",   cmd_players,   filters=group_filter))
    app.add_handler(CommandHandler("stopgame",  cmd_stopgame,  filters=group_filter))

    # Callbacks
    app.add_handler(CallbackQueryHandler(cb_game, pattern=r"^game:"))
    app.add_handler(CallbackQueryHandler(cb_tod,  pattern=r"^tod:"))
    app.add_handler(CallbackQueryHandler(cb_wyr,  pattern=r"^wyr:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.job_queue.run_repeating(job_proactive, interval=6 * 3600, first=300)

    return app


async def set_bot_commands(app: Application):
    from telegram import BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

    # Private chat — includes panel for admins
    await app.bot.set_my_commands([
        BotCommand("start",       "wake up"),
        BotCommand("help",        "what can you do"),
        BotCommand("mode",        "switch personality"),
        BotCommand("memory",      "what i know about you"),
        BotCommand("clearmemory", "wipe my memory of you"),
        BotCommand("clear",       "clear chat history"),
        BotCommand("stats",       "your stats"),
        BotCommand("panel",       "admin panel 🎛"),
    ], scope=BotCommandScopeAllPrivateChats())

    # Group chat — only fun/visible commands shown
    # Admin commands (ban/mute/warn etc) are intentionally hidden from menu
    await app.bot.set_my_commands([
        BotCommand("couple",   "couple of the day 💑"),
        BotCommand("game",     "group games 🎮"),
        BotCommand("join",     "join active game"),
        BotCommand("leave",    "leave active game"),
        BotCommand("players",  "who's in the game"),
        BotCommand("stopgame", "stop active game"),
        BotCommand("notes",    "list saved notes"),
        BotCommand("filters",  "list word filters"),
    ], scope=BotCommandScopeAllGroupChats())
