"""
group_commands.py — Group-only commands: admin tools + fun features.

Admin commands (only usable by Telegram group admins):
  /ban   — ban a user from the group
  /unban — unban a user
  /mute  — mute a user (restrict messages)
  /unmute — unmute a user
  /kick  — kick a user (they can rejoin)
  /warn  — warn a user (3 warns = auto-ban)
  /warns — check warn count for a user
  /pin   — pin the replied-to message

Fun group commands (usable by everyone):
  /couple — generate couple of the day (once per day per group)
  /game   — show list of playable group games with start buttons

All these commands are registered with group filter so they
never appear or work in private chats with the bot.
"""

import random
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from app.database import AsyncSessionLocal
from app.crud import (
    add_warn, get_warn_count, reset_warns,
    get_couple_of_day, save_couple_of_day,
)
from app.llm import get_ai_response

logger = logging.getLogger(__name__)

WARNS_BEFORE_BAN = 3


# ── Helper: check if caller is a group admin ──────────────────────────────────

async def _is_admin(update: Update, context) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


async def _get_target(update: Update, context) -> tuple | None:
    """
    Get the target user from a reply or @mention argument.
    Returns (user_id, name) or None with an error message sent.
    """
    # From reply
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        return target.id, target.first_name or target.username or str(target.id)

    # From argument: /ban @username or /ban userid
    if context.args:
        arg = context.args[0].lstrip("@")
        try:
            uid = int(arg)
            return uid, str(uid)
        except ValueError:
            try:
                member = await context.bot.get_chat_member(update.effective_chat.id, arg)
                u = member.user
                return u.id, u.first_name or u.username or arg
            except Exception:
                await update.message.reply_text("can't find that user")
                return None

    await update.message.reply_text("reply to a message or give a username")
    return None


# ── /ban ──────────────────────────────────────────────────────────────────────

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else None

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, uid)
        msg = f"🔨 {name} got banned"
        if reason:
            msg += f" — {reason}"
        await update.message.reply_text(msg)
    except BadRequest as e:
        await update.message.reply_text(f"couldn't ban: {e.message}")


# ── /unban ────────────────────────────────────────────────────────────────────

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    try:
        await context.bot.unban_chat_member(update.effective_chat.id, uid, only_if_banned=True)
        await update.message.reply_text(f"✅ {name} is unbanned")
    except BadRequest as e:
        await update.message.reply_text(f"couldn't unban: {e.message}")


# ── /kick ─────────────────────────────────────────────────────────────────────

async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, uid)
        await context.bot.unban_chat_member(update.effective_chat.id, uid)
        await update.message.reply_text(f"👟 {name} got kicked. they can rejoin tho")
    except BadRequest as e:
        await update.message.reply_text(f"couldn't kick: {e.message}")


# ── /mute ─────────────────────────────────────────────────────────────────────

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    # Parse duration from args: /mute @user 10m or /mute @user 1h
    until = None
    duration_str = ""
    for arg in (context.args or []):
        if arg.endswith("m") and arg[:-1].isdigit():
            until = datetime.utcnow() + timedelta(minutes=int(arg[:-1]))
            duration_str = f" for {arg[:-1]} minutes"
            break
        elif arg.endswith("h") and arg[:-1].isdigit():
            until = datetime.utcnow() + timedelta(hours=int(arg[:-1]))
            duration_str = f" for {arg[:-1]} hours"
            break
        elif arg.endswith("d") and arg[:-1].isdigit():
            until = datetime.utcnow() + timedelta(days=int(arg[:-1]))
            duration_str = f" for {arg[:-1]} days"
            break

    try:
        perms = ChatPermissions(
            can_send_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        )
        await context.bot.restrict_chat_member(
            update.effective_chat.id, uid,
            permissions=perms,
            until_date=until,
        )
        await update.message.reply_text(f"🔇 {name} is muted{duration_str}")
    except BadRequest as e:
        await update.message.reply_text(f"couldn't mute: {e.message}")


# ── /unmute ───────────────────────────────────────────────────────────────────

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    try:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False,
        )
        await context.bot.restrict_chat_member(
            update.effective_chat.id, uid, permissions=perms
        )
        await update.message.reply_text(f"🔊 {name} can talk again")
    except BadRequest as e:
        await update.message.reply_text(f"couldn't unmute: {e.message}")


# ── /warn ─────────────────────────────────────────────────────────────────────

async def cmd_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    reason = " ".join(context.args[1:]) if context.args and len(context.args) > 1 else None

    async with AsyncSessionLocal() as db:
        warn_count = await add_warn(
            db, uid, update.effective_chat.id,
            update.effective_user.id, reason,
        )

    if warn_count >= WARNS_BEFORE_BAN:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, uid)
            async with AsyncSessionLocal() as db:
                await reset_warns(db, uid, update.effective_chat.id)
            msg = f"⛔ {name} got {warn_count} warnings and is now banned. bye 👋"
        except BadRequest:
            msg = f"⚠️ {name} hit {warn_count} warnings but I couldn't ban them — check my permissions"
    else:
        remaining = WARNS_BEFORE_BAN - warn_count
        msg = f"⚠️ {name} warned ({warn_count}/{WARNS_BEFORE_BAN})"
        if reason:
            msg += f" — {reason}"
        msg += f"\n{remaining} more warn{'s' if remaining > 1 else ''} = ban"

    await update.message.reply_text(msg)


# ── /warns ────────────────────────────────────────────────────────────────────

async def cmd_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target

    async with AsyncSessionLocal() as db:
        count = await get_warn_count(db, uid, update.effective_chat.id)

    if count == 0:
        await update.message.reply_text(f"{name} has no warnings ✅")
    else:
        await update.message.reply_text(
            f"{name} has {count}/{WARNS_BEFORE_BAN} warnings"
        )


# ── /pin ─────────────────────────────────────────────────────────────────────

async def cmd_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("reply to the message you want to pin")
        return

    try:
        await context.bot.pin_chat_message(
            update.effective_chat.id,
            update.message.reply_to_message.message_id,
            disable_notification=False,
        )
        await update.message.reply_text("📌 pinned")
    except BadRequest as e:
        await update.message.reply_text(f"couldn't pin: {e.message}")


# ── /couple ───────────────────────────────────────────────────────────────────

async def cmd_couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Check if already generated today
    async with AsyncSessionLocal() as db:
        existing = await get_couple_of_day(db, chat_id)

    if existing:
        await update.message.reply_text(
            f"💑 today's couple already dropped:\n"
            f"@{existing.user1_name} & @{existing.user2_name} 💕\n"
            f"come back tomorrow for a new one"
        )
        return

    # Get recent members from chat (from recent messages)
    # We collect from context.bot_data if available, otherwise use
    # the message sender + reply target as a pool
    try:
        # Try to get admins as a base member pool
        admins = await context.bot.get_chat_administrators(chat_id)
        members = [a.user for a in admins if not a.user.is_bot]
    except Exception:
        members = []

    # Add the current user to pool if not already there
    cur_user = update.effective_user
    if not any(m.id == cur_user.id for m in members):
        members.append(cur_user)

    # Need at least 2 people
    if len(members) < 2:
        await update.message.reply_text(
            "not enough people in here for a couple 😭 need at least 2"
        )
        return

    # Pick 2 random unique members
    chosen = random.sample(members, 2)
    u1, u2 = chosen[0], chosen[1]
    name1 = u1.first_name or u1.username or "Mystery Person"
    name2 = u2.first_name or u2.username or "Mystery Person"

    # Generate the couple message via LLM
    prompt = (
        f"Generate a short, funny, slightly romantic couple announcement for a Telegram group. "
        f"The couple of the day is {name1} and {name2}. "
        f"Mention both of them. Keep it 2-3 sentences max. "
        f"Mix humor and romance. Use emojis. "
        f"Do NOT use markdown. Plain text only. "
        f"Write in the same language as this instruction (English) unless the group usually speaks another language."
    )

    try:
        from app import providers
        caption = await providers.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.95,
            tier="fast",
        )
    except Exception:
        caption = f"{name1} and {name2} are today's couple 💕 nobody asked but here we are 😭"

    # Save to DB
    async with AsyncSessionLocal() as db:
        await save_couple_of_day(
            db, chat_id,
            u1.id, u2.id,
            u1.username or name1,
            u2.username or name2,
        )

    # Send with mentions
    text = f"💑 COUPLE OF THE DAY 💑\n\n{caption}"
    await update.message.reply_text(text)


# ── /game ─────────────────────────────────────────────────────────────────────

async def cmd_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of group games with pressable start buttons."""
    keyboard = [
        [InlineKeyboardButton("🎯 Truth or Dare",     callback_data="game:tod")],
        [InlineKeyboardButton("❓ Trivia Battle",      callback_data="game:trivia")],
        [InlineKeyboardButton("🔢 Number Guess",       callback_data="game:numguess")],
        [InlineKeyboardButton("🎭 Would You Rather",   callback_data="game:wyr")],
        [InlineKeyboardButton("🔤 Word Chain",         callback_data="game:wordchain")],
    ]
    await update.message.reply_text(
        "🎮 pick a game to start:\n\n"
        "Truth or Dare — classic, the bot asks\n"
        "Trivia Battle — answer fastest wins\n"
        "Number Guess — 1 to 100, bot picks\n"
        "Would You Rather — group votes\n"
        "Word Chain — each person continues from last letter",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cb_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle game selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    game = query.data.split(":", 1)[1]

    game_intros = {
        "tod": (
            "🎯 Truth or Dare!\n\n"
            "Reply to this message to join. "
            "Once everyone's in, reply /startgame to begin.\n"
            "Bot will ask each person truth or dare randomly."
        ),
        "trivia": (
            "❓ Trivia Battle!\n\n"
            "Bot asks questions one by one. "
            "First person to reply with the correct answer wins the point.\n"
            "Reply /startgame to kick it off."
        ),
        "numguess": (
            "🔢 Number Guess!\n\n"
            "I'm thinking of a number between 1 and 100.\n"
            "Everyone guess — first correct answer wins 🏆\n\n"
            f"My number is locked in. Start guessing 👇"
        ),
        "wyr": (
            "🎭 Would You Rather!\n\n"
            "Bot gives the group a dilemma. Everyone votes.\n"
            "Reply /startgame to get the first question."
        ),
        "wordchain": (
            "🔤 Word Chain!\n\n"
            "Rules: each word must start with the last letter of the previous word.\n"
            "No repeats. Bot tracks and calls out cheaters 👀\n"
            "First word: CHAOS\nYour turn 👇"
        ),
    }

    # For number guess, also store the secret number
    if game == "numguess":
        secret = random.randint(1, 100)
        context.chat_data["numguess_secret"] = secret
        context.chat_data["numguess_active"] = True

    # For word chain, store the current word
    if game == "wordchain":
        context.chat_data["wordchain_active"] = True
        context.chat_data["wordchain_current"] = "chaos"
        context.chat_data["wordchain_used"] = {"chaos"}

    intro = game_intros.get(game, "game starting...")
    await query.edit_message_text(intro)


async def handle_game_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if a group message is part of an active game.
    Returns True if handled (so bot.py skips normal processing).
    """
    if not update.message or not update.message.text:
        return False

    text = update.message.text.strip().lower()
    chat_data = context.chat_data

    # ── Number guess game ──────────────────────────────────────────────────
    if chat_data.get("numguess_active"):
        try:
            guess = int(text)
            secret = chat_data.get("numguess_secret", 50)
            name = update.effective_user.first_name or "you"

            if guess == secret:
                chat_data["numguess_active"] = False
                await update.message.reply_text(
                    f"🎉 {name} got it! the number was {secret}!\nngl that was impressive 🔥"
                )
                return True
            elif guess < secret:
                await update.message.reply_text(f"higher 📈")
                return True
            else:
                await update.message.reply_text(f"lower 📉")
                return True
        except ValueError:
            pass   # Not a number, let normal handling continue

    # ── Word chain game ────────────────────────────────────────────────────
    if chat_data.get("wordchain_active"):
        words = text.split()
        if len(words) == 1:   # Single word responses only
            word = words[0]
            current = chat_data.get("wordchain_current", "")
            used = chat_data.get("wordchain_used", set())

            if not current:
                return False

            if word in used:
                await update.message.reply_text(f"❌ '{word}' already used 💀")
                return True

            if word[0] != current[-1]:
                await update.message.reply_text(
                    f"❌ word must start with '{current[-1].upper()}' not '{word[0].upper()}'"
                )
                return True

            # Valid word
            chat_data["wordchain_current"] = word
            used.add(word)
            chat_data["wordchain_used"] = used
            await update.message.reply_text(f"✅ '{word}' — next word must start with '{word[-1].upper()}'")
            return True

    return False
