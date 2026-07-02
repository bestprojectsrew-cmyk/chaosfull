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

    # Track which game is active + reset the player roster (used by
    # /join, /leave, /players, /stopgame)
    context.chat_data["gc_active_game"] = game
    context.chat_data["gc_players"] = {}

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

    # Truth or Dare — attach playable buttons right away
    if game == "tod":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🎯 Truth", callback_data="tod:truth"),
            InlineKeyboardButton("🎲 Dare",  callback_data="tod:dare"),
        ]])
        await query.edit_message_text(intro, reply_markup=keyboard)
        return

    # Would You Rather — pick a dilemma and attach vote buttons
    if game == "wyr":
        a, b = random.choice(WYR_QUESTIONS)
        context.chat_data["wyr_current"] = (a, b)
        context.chat_data["wyr_votes"] = {"a": set(), "b": set()}
        text = f"{intro}\n\n🅰️ {a}\n\n🅱️ {b}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🅰️ Vote A", callback_data="wyr:a"),
             InlineKeyboardButton("🅱️ Vote B", callback_data="wyr:b")],
            [InlineKeyboardButton("🔄 New Question", callback_data="wyr:new")],
        ])
        await query.edit_message_text(text, reply_markup=keyboard)
        return

    await query.edit_message_text(intro)


async def handle_game_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handle active games.
    Returns True only if a message was actually consumed by a game.
    Returns False to let the normal AI continue.
    """

    if not update.message or not update.message.text:
        return False

    text = update.message.text.strip()
    lower = text.lower()

    chat_data = context.chat_data

    EXIT_WORDS = {
        "/exit",
        "exit",
        "quit",
        "leave",
        "cancel",
        "stop",
        "stop game",
        "end",
        "end game",
    }

    # ------------------------
    # Exit any running game
    # ------------------------
    if lower in EXIT_WORDS:
        chat_data.pop("numguess_active", None)
        chat_data.pop("numguess_secret", None)

        chat_data.pop("wordchain_active", None)
        chat_data.pop("wordchain_current", None)
        chat_data.pop("wordchain_used", None)

        chat_data.pop("wyr_current", None)
        chat_data.pop("wyr_votes", None)

        chat_data.pop("gc_active_game", None)
        chat_data.pop("gc_players", None)

        await update.message.reply_text("✅ Game ended.")
        return True

    # ------------------------
    # Number Guess
    # ------------------------
    if chat_data.get("numguess_active"):

        if not lower.isdigit():
            chat_data.pop("numguess_active", None)
            chat_data.pop("numguess_secret", None)
            return False

        guess = int(lower)
        secret = chat_data.get("numguess_secret", 50)

        if guess == secret:
            chat_data.pop("numguess_active", None)
            chat_data.pop("numguess_secret", None)

            await update.message.reply_text(
                f"🎉 Correct! The number was {secret}."
            )
            return True

        elif guess < secret:
            await update.message.reply_text("📈 Higher")
            return True

        else:
            await update.message.reply_text("📉 Lower")
            return True

    # ------------------------
    # Word Chain
    # ------------------------
    if chat_data.get("wordchain_active"):

        words = lower.split()

        # User clearly changed topic
        if len(words) != 1:

            chat_data.pop("wordchain_active", None)
            chat_data.pop("wordchain_current", None)
            chat_data.pop("wordchain_used", None)

            return False

        word = words[0]

        # Ignore commands
        if word.startswith("/"):
            chat_data.pop("wordchain_active", None)
            chat_data.pop("wordchain_current", None)
            chat_data.pop("wordchain_used", None)
            return False

        current = chat_data.get("wordchain_current")

        if not current:
            return False

        used = chat_data.get("wordchain_used", set())

        if word in used:
            await update.message.reply_text("❌ Already used.")
            return True

        expected = current[-1].lower()

        if word[0].lower() != expected:
            await update.message.reply_text(
                f"❌ Word must start with '{expected.upper()}'."
            )
            return True

        used.add(word)

        chat_data["wordchain_used"] = used
        chat_data["wordchain_current"] = word

        await update.message.reply_text(
            f"✅ Nice! Next word starts with '{word[-1].upper()}'."
        )

        return True

    return False


# ── Additional admin commands ─────────────────────────────────────────────────

async def cmd_promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, uid,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_invite_users=True,
        )
        await update.message.reply_text(f"⬆️ {name} promoted to admin")
    except Exception as e:
        await update.message.reply_text(f"couldn't promote: {e}")


async def cmd_demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    target = await _get_target(update, context)
    if not target:
        return
    uid, name = target
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, uid,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_invite_users=False,
            can_change_info=False,
            can_manage_chat=False,
        )
        await update.message.reply_text(f"⬇️ {name} demoted")
    except Exception as e:
        await update.message.reply_text(f"couldn't demote: {e}")


async def cmd_purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    count = 10
    if context.args:
        try:
            count = min(int(context.args[0]), 100)
        except ValueError:
            pass
    deleted = 0
    msg_id = update.message.message_id
    for i in range(msg_id, msg_id - count - 1, -1):
        try:
            await context.bot.delete_message(update.effective_chat.id, i)
            deleted += 1
        except Exception:
            pass
    try:
        m = await update.effective_chat.send_message(f"🗑 purged {deleted} messages")
        import asyncio
        await asyncio.sleep(3)
        await m.delete()
    except Exception:
        pass


async def cmd_lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    try:
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(can_send_messages=False),
        )
        await update.message.reply_text("🔒 group locked — only admins can send messages")
    except Exception as e:
        await update.message.reply_text(f"couldn't lock: {e}")


async def cmd_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    try:
        await context.bot.set_chat_permissions(
            update.effective_chat.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_invite_users=True,
            ),
        )
        await update.message.reply_text("🔓 group unlocked")
    except Exception as e:
        await update.message.reply_text(f"couldn't unlock: {e}")


async def cmd_slowmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    seconds = 0
    if context.args:
        try:
            seconds = int(context.args[0])
        except ValueError:
            await update.message.reply_text("usage: /slowmode 30 (seconds, 0 to disable)")
            return
    try:
        await context.bot.set_chat_slow_mode_delay(update.effective_chat.id, seconds)
        if seconds == 0:
            await update.message.reply_text("⏱ slowmode disabled")
        else:
            await update.message.reply_text(f"⏱ slowmode set to {seconds}s")
    except Exception as e:
        await update.message.reply_text(f"couldn't set slowmode: {e}")


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        await update.message.reply_text(
            f"User ID: {target.id}\nChat ID: {update.effective_chat.id}"
        )
    else:
        await update.message.reply_text(
            f"Your ID: {user.id}\nChat ID: {update.effective_chat.id}"
        )


async def cmd_userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        target = update.effective_user
    name = f"{target.first_name or ''} {target.last_name or ''}".strip()
    username = f"@{target.username}" if target.username else "no username"
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, target.id)
        status = member.status
    except Exception:
        status = "unknown"
    await update.message.reply_text(
        f"👤 User Info\n\n"
        f"Name: {name}\n"
        f"Username: {username}\n"
        f"ID: {target.id}\n"
        f"Status: {status}\n"
        f"Bot: {'yes' if target.is_bot else 'no'}"
    )


async def cmd_chatinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    try:
        count = await context.bot.get_chat_member_count(chat.id)
    except Exception:
        count = "unknown"
    await update.message.reply_text(
        f"💬 Chat Info\n\n"
        f"Name: {chat.title or 'N/A'}\n"
        f"ID: {chat.id}\n"
        f"Type: {chat.type}\n"
        f"Members: {count}\n"
        f"Username: @{chat.username}" if chat.username else f"ID: {chat.id}"
    )


# ── Word filters ────────────────────────────────────────────────────────────
#
# Filters are stored per-chat in context.chat_data (in-memory, resets on
# restart). Keyed by lowercase trigger phrase -> response text.
#
#   /filter trigger | response text
#   /filter trigger              (reply to the message you want saved)
#   /delfilter trigger
#   /filters                     (list triggers)

async def cmd_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    raw = " ".join(context.args) if context.args else ""

    if "|" in raw:
        trigger, response = raw.split("|", 1)
        trigger = trigger.strip().lower()
        response = response.strip()
    elif update.message.reply_to_message and context.args:
        trigger = raw.strip().lower()
        response = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        if not response:
            await update.message.reply_text("that message has no text to save as a filter")
            return
    else:
        await update.message.reply_text(
            "usage: /filter trigger | response\n"
            "or reply to a message with /filter trigger"
        )
        return

    if not trigger:
        await update.message.reply_text("need a trigger word")
        return

    filters_map = context.chat_data.setdefault("filters", {})
    filters_map[trigger] = response
    await update.message.reply_text(f"✅ filter saved: \"{trigger}\"")


async def cmd_delfilter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    if not context.args:
        await update.message.reply_text("usage: /delfilter trigger")
        return

    trigger = " ".join(context.args).strip().lower()
    filters_map = context.chat_data.setdefault("filters", {})
    if trigger in filters_map:
        del filters_map[trigger]
        await update.message.reply_text(f"🗑 filter \"{trigger}\" removed")
    else:
        await update.message.reply_text("no filter by that name")


async def cmd_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters_map = context.chat_data.get("filters", {})
    if not filters_map:
        await update.message.reply_text("no filters set in this chat")
        return
    lines = ["📋 active filters:\n"] + [f"• {t}" for t in sorted(filters_map)]
    await update.message.reply_text("\n".join(lines))


async def handle_filter_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check message text against saved filters. Returns True if a filter fired."""
    if not update.message or not update.message.text:
        return False

    filters_map = context.chat_data.get("filters", {})
    if not filters_map:
        return False

    text = update.message.text.lower()
    for trigger, response in filters_map.items():
        if trigger in text:
            await update.message.reply_text(response)
            return True
    return False


# ── Notes ────────────────────────────────────────────────────────────────────
#
# Notes are stored per-chat in context.chat_data (in-memory), keyed by
# lowercase note name -> content. Retrieve with /getnote name or the
# #notename hashtag shortcut.

async def cmd_savenote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return

    raw = " ".join(context.args) if context.args else ""

    if "|" in raw:
        name, content = raw.split("|", 1)
        name = name.strip().lower()
        content = content.strip()
    elif update.message.reply_to_message and context.args:
        name = raw.strip().lower()
        content = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        if not content:
            await update.message.reply_text("that message has no text to save as a note")
            return
    else:
        await update.message.reply_text(
            "usage: /savenote name | content\n"
            "or reply to a message with /savenote name"
        )
        return

    if not name:
        await update.message.reply_text("need a note name")
        return

    notes_map = context.chat_data.setdefault("notes", {})
    notes_map[name] = content
    await update.message.reply_text(f"📝 note saved: \"{name}\" (get it with #{name} or /getnote {name})")


async def cmd_getnote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("usage: /getnote name")
        return
    name = " ".join(context.args).strip().lower()
    notes_map = context.chat_data.get("notes", {})
    if name in notes_map:
        await update.message.reply_text(notes_map[name])
    else:
        await update.message.reply_text("no note by that name")


async def cmd_delnote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only 💀")
        return
    if not context.args:
        await update.message.reply_text("usage: /delnote name")
        return
    name = " ".join(context.args).strip().lower()
    notes_map = context.chat_data.setdefault("notes", {})
    if name in notes_map:
        del notes_map[name]
        await update.message.reply_text(f"🗑 note \"{name}\" removed")
    else:
        await update.message.reply_text("no note by that name")


async def cmd_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes_map = context.chat_data.get("notes", {})
    if not notes_map:
        await update.message.reply_text("no notes saved in this chat")
        return
    lines = ["📋 saved notes:\n"] + [f"• #{n}" for n in sorted(notes_map)]
    lines.append("\nget one with #name or /getnote name")
    await update.message.reply_text("\n".join(lines))


async def handle_hashtag_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle #notename shortcut. Returns True if a note was found and sent."""
    if not update.message or not update.message.text:
        return False

    text = update.message.text.strip()
    if not text.startswith("#") or len(text) < 2:
        return False

    name = text[1:].split()[0].lower()
    notes_map = context.chat_data.get("notes", {})
    if name in notes_map:
        await update.message.reply_text(notes_map[name])
        return True
    return False


# ── Game roster: /join /leave /players /stopgame ────────────────────────────
#
# Works alongside cb_game, which sets chat_data["gc_active_game"] and resets
# chat_data["gc_players"] whenever a game is started from the /game menu.

async def cmd_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    game = chat_data.get("gc_active_game")
    if not game:
        await update.message.reply_text("no active game right now — start one with /game")
        return

    players = chat_data.setdefault("gc_players", {})
    user = update.effective_user
    if user.id in players:
        await update.message.reply_text("you're already in 👍")
        return

    players[user.id] = user.first_name or user.username or str(user.id)
    await update.message.reply_text(
        f"✅ {players[user.id]} joined ({len(players)} player{'s' if len(players) != 1 else ''} in)"
    )


async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    players = chat_data.get("gc_players", {})
    user = update.effective_user
    if user.id not in players:
        await update.message.reply_text("you're not in the current game")
        return
    name = players.pop(user.id)
    await update.message.reply_text(f"👋 {name} left the game")


async def cmd_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    game = chat_data.get("gc_active_game")
    players = chat_data.get("gc_players", {})
    if not game:
        await update.message.reply_text("no active game right now")
        return
    if not players:
        await update.message.reply_text("no one's joined yet — /join to hop in")
        return
    lines = [f"🎮 players ({len(players)}):\n"] + [f"• {n}" for n in players.values()]
    await update.message.reply_text("\n".join(lines))


async def cmd_stopgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    was_active = any(
        chat_data.get(k)
        for k in ("gc_active_game", "numguess_active", "wordchain_active", "wyr_current")
    )
    if not was_active:
        await update.message.reply_text("no active game to stop")
        return

    for key in (
        "gc_active_game", "gc_players",
        "numguess_active", "numguess_secret",
        "wordchain_active", "wordchain_current", "wordchain_used",
        "wyr_current", "wyr_votes",
    ):
        chat_data.pop(key, None)

    await update.message.reply_text("🛑 game stopped")


# ── Truth or Dare / Would You Rather content ─────────────────────────────────

TRUTH_QUESTIONS = [
    "what's the most embarrassing thing in your search history?",
    "what's a lie you told that you never got caught for?",
    "who in this chat would you trust with a secret?",
    "what's the worst gift you've ever received?",
    "what's your most unpopular opinion?",
    "what's the last thing you lied about to your parents?",
    "what app do you spend the most time on that you're not proud of?",
]

DARE_CHALLENGES = [
    "send the last photo in your camera roll (no explanation)",
    "type with your elbows for the next message",
    "let the group pick your profile picture for the next hour",
    "text your crush/ex \"hey\" and post the reply here",
    "speak only in questions for the next 3 messages",
    "send a voice message singing your favorite song's chorus",
    "compliment 3 people in this chat right now",
]

WYR_QUESTIONS = [
    ("have to sing everything you say for a week", "have to whisper everything you say for a week"),
    ("be able to fly but only 3 feet off the ground", "be invisible but only when no one is looking"),
    ("never use social media again", "never watch another movie or show again"),
    ("always be 10 minutes late", "always be 20 minutes early"),
    ("have unlimited money but no friends", "have amazing friends but be broke forever"),
    ("lose all your memories from the past year", "never make a new memory again"),
    ("be famous but broke", "be rich but unknown"),
]


# ── Truth or Dare callback ────────────────────────────────────────────────────

async def cb_tod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data.split(":", 1)[1]
    player = query.from_user.first_name or query.from_user.username or "player"

    if choice == "truth":
        prompt = random.choice(TRUTH_QUESTIONS)
        text = f"🎯 Truth for {player}:\n\n{prompt}"
    else:
        prompt = random.choice(DARE_CHALLENGES)
        text = f"🎲 Dare for {player}:\n\n{prompt}"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎯 Truth", callback_data="tod:truth"),
        InlineKeyboardButton("🎲 Dare",  callback_data="tod:dare"),
    ]])
    await query.edit_message_text(text, reply_markup=keyboard)


# ── Would You Rather callback ─────────────────────────────────────────────────

async def cb_wyr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data.split(":", 1)[1]
    chat_data = context.chat_data

    if choice == "new":
        await query.answer()
        a, b = random.choice(WYR_QUESTIONS)
        chat_data["wyr_current"] = (a, b)
        chat_data["wyr_votes"] = {"a": set(), "b": set()}
        text = f"🎭 Would You Rather\n\n🅰️ {a}\n\n🅱️ {b}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🅰️ Vote A", callback_data="wyr:a"),
             InlineKeyboardButton("🅱️ Vote B", callback_data="wyr:b")],
            [InlineKeyboardButton("🔄 New Question", callback_data="wyr:new")],
        ])
        await query.edit_message_text(text, reply_markup=keyboard)
        return

    current = chat_data.get("wyr_current")
    if not current:
        await query.answer("no active round — start a new one", show_alert=True)
        return

    votes = chat_data.setdefault("wyr_votes", {"a": set(), "b": set()})
    uid = query.from_user.id
    votes["a"].discard(uid)
    votes["b"].discard(uid)
    votes[choice].add(uid)
    await query.answer(f"you voted {choice.upper()}")

    a, b = current
    text = (
        f"🎭 Would You Rather\n\n"
        f"🅰️ {a}  ({len(votes['a'])} votes)\n\n"
        f"🅱️ {b}  ({len(votes['b'])} votes)"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🅰️ Vote A", callback_data="wyr:a"),
         InlineKeyboardButton("🅱️ Vote B", callback_data="wyr:b")],
        [InlineKeyboardButton("🔄 New Question", callback_data="wyr:new")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard)
