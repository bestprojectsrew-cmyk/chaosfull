"""
moderation/admin_panel.py — Rose Bot style admin panel in private chat.

/panel — opens interactive menu for group admins
Shows: Moderation | Filters | Notes | Games | Stats | Settings | AI
Each section uses inline keyboards. Only works if user is admin of a group.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.database import AsyncSessionLocal
from app.crud import get_filters, list_notes, get_warn_count

logger = logging.getLogger(__name__)


def _main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔨 Moderation",  callback_data="panel:mod"),
         InlineKeyboardButton("🔍 Filters",     callback_data="panel:filters")],
        [InlineKeyboardButton("📝 Notes",        callback_data="panel:notes"),
         InlineKeyboardButton("🎮 Games",        callback_data="panel:games")],
        [InlineKeyboardButton("📊 Stats",        callback_data="panel:stats"),
         InlineKeyboardButton("⚙️ Settings",    callback_data="panel:settings")],
        [InlineKeyboardButton("🤖 AI",           callback_data="panel:ai")],
    ])


def _back_button() -> list:
    return [[InlineKeyboardButton("⬅️ Back", callback_data="panel:main")]]


async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open the admin panel — private chat only."""
    if update.effective_chat.type != "private":
        await update.message.reply_text("use /panel in our private chat, not in the group")
        return

    await update.message.reply_text(
        "🎛 Chaoz Admin Panel\n\nManage your groups from here:",
        reply_markup=_main_menu(),
    )


async def cb_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    section = query.data.split(":", 1)[1]

    if section == "main":
        await query.edit_message_text(
            "🎛 Chaoz Admin Panel\n\nManage your groups from here:",
            reply_markup=_main_menu(),
        )

    elif section == "mod":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔨 /ban",      callback_data="panel:cmd:ban"),
             InlineKeyboardButton("✅ /unban",     callback_data="panel:cmd:unban")],
            [InlineKeyboardButton("👟 /kick",      callback_data="panel:cmd:kick"),
             InlineKeyboardButton("🔇 /mute",      callback_data="panel:cmd:mute")],
            [InlineKeyboardButton("🔊 /unmute",    callback_data="panel:cmd:unmute"),
             InlineKeyboardButton("⚠️ /warn",     callback_data="panel:cmd:warn")],
            [InlineKeyboardButton("🗑 /purge",     callback_data="panel:cmd:purge"),
             InlineKeyboardButton("📌 /pin",       callback_data="panel:cmd:pin")],
            [InlineKeyboardButton("🔒 /lock",      callback_data="panel:cmd:lock"),
             InlineKeyboardButton("🔓 /unlock",    callback_data="panel:cmd:unlock")],
            [InlineKeyboardButton("⏱ /slowmode",   callback_data="panel:cmd:slowmode"),
             InlineKeyboardButton("⬆️ /promote",   callback_data="panel:cmd:promote")],
            *_back_button()
        ])
        await query.edit_message_text(
            "🔨 Moderation Commands\n\nAll commands work in group chat.\nReply to a user's message or add @username after the command:",
            reply_markup=keyboard,
        )

    elif section == "filters":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ /filter <word> <reply>",    callback_data="panel:cmd:filter")],
            [InlineKeyboardButton("❌ /delfilter <word>",          callback_data="panel:cmd:delfilter")],
            [InlineKeyboardButton("📋 /filters (list all)",        callback_data="panel:cmd:filters")],
            *_back_button()
        ])
        await query.edit_message_text(
            "🔍 Filter System\n\n"
            "Set automatic responses when keywords are used in your group.\n\n"
            "Example:\n/filter england Water bottle 😭\n\n"
            "Now whenever someone says 'england' the bot replies 'Water bottle 😭'",
            reply_markup=keyboard,
        )

    elif section == "notes":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💾 /savenote <name> <text>",   callback_data="panel:cmd:savenote")],
            [InlineKeyboardButton("📖 /getnote <name> or #name",  callback_data="panel:cmd:getnote")],
            [InlineKeyboardButton("🗑 /delnote <name>",           callback_data="panel:cmd:delnote")],
            [InlineKeyboardButton("📋 /notes (list all)",          callback_data="panel:cmd:notes")],
            *_back_button()
        ])
        await query.edit_message_text(
            "📝 Notes System\n\n"
            "Save useful info for your group that anyone can retrieve.\n\n"
            "Example:\n/savenote rules 1. Be respectful. 2. No spam.\n\n"
            "Anyone can get it with: /getnote rules or just #rules",
            reply_markup=keyboard,
        )

    elif section == "games":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 /game — start a game",      callback_data="panel:cmd:game")],
            [InlineKeyboardButton("🛑 /stopgame — stop game",     callback_data="panel:cmd:stopgame")],
            [InlineKeyboardButton("👥 /players — who's joined",   callback_data="panel:cmd:players")],
            [InlineKeyboardButton("💑 /couple — couple of day",   callback_data="panel:cmd:couple")],
            *_back_button()
        ])
        await query.edit_message_text(
            "🎮 Group Games\n\nAll games run in the group chat.",
            reply_markup=keyboard,
        )

    elif section == "stats":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ℹ️ /chatinfo",    callback_data="panel:cmd:chatinfo")],
            [InlineKeyboardButton("👤 /userinfo",    callback_data="panel:cmd:userinfo")],
            [InlineKeyboardButton("🆔 /id",          callback_data="panel:cmd:id")],
            *_back_button()
        ])
        await query.edit_message_text(
            "📊 Statistics & Info Commands",
            reply_markup=keyboard,
        )

    elif section == "settings":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 AI Mode: ON/OFF",    callback_data="panel:cmd:aimode")],
            [InlineKeyboardButton("🌍 Language detection", callback_data="panel:cmd:lang")],
            *_back_button()
        ])
        await query.edit_message_text(
            "⚙️ Group Settings",
            reply_markup=keyboard,
        )

    elif section == "ai":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎭 /mode — personality", callback_data="panel:cmd:mode")],
            [InlineKeyboardButton("🧠 /memory",             callback_data="panel:cmd:memory")],
            [InlineKeyboardButton("🗑 /clearmemory",        callback_data="panel:cmd:clearmemory")],
            *_back_button()
        ])
        await query.edit_message_text(
            "🤖 AI Settings",
            reply_markup=keyboard,
        )

    elif section.startswith("cmd:"):
        cmd = section.split(":", 1)[1]
        usage_map = {
            "ban":         "/ban — reply to message or: /ban @username [reason]",
            "unban":       "/unban — reply or: /unban @username",
            "kick":        "/kick — reply or: /kick @username",
            "mute":        "/mute — reply or: /mute @username 10m/1h/1d",
            "unmute":      "/unmute — reply or: /unmute @username",
            "warn":        "/warn — reply or: /warn @username [reason]",
            "purge":       "/purge N — deletes last N messages",
            "pin":         "/pin — reply to the message you want pinned",
            "lock":        "/lock — prevents members from sending messages",
            "unlock":      "/unlock — restores member permissions",
            "slowmode":    "/slowmode 30 — sets 30 second slowmode (0 to disable)",
            "promote":     "/promote — reply or: /promote @username",
            "filter":      "/filter <word> <reply text>",
            "delfilter":   "/delfilter <word>",
            "filters":     "/filters — lists all active filters",
            "savenote":    "/savenote <name> <content>",
            "getnote":     "/getnote <name>  or just type #name in chat",
            "delnote":     "/delnote <name>",
            "notes":       "/notes — lists all saved notes",
            "game":        "/game — shows game picker in group",
            "stopgame":    "/stopgame — stops whatever game is running",
            "players":     "/players — shows who has joined the current game",
            "couple":      "/couple — generates couple of the day (once per day)",
            "chatinfo":    "/chatinfo — shows group info",
            "userinfo":    "/userinfo — reply to see user info",
            "id":          "/id — shows your Telegram ID",
            "mode":        "/mode — pick bot personality",
            "memory":      "/memory — see what bot remembers about you",
            "clearmemory": "/clearmemory — wipe bot's memory",
            "aimode":      "coming soon",
            "lang":        "language is detected automatically per message",
        }
        usage = usage_map.get(cmd, f"/{cmd} — use this command in your group")
        keyboard = InlineKeyboardMarkup(_back_button())
        await query.edit_message_text(
            f"📖 How to use:\n\n{usage}\n\nGo to your group and type the command.",
            reply_markup=keyboard,
        )
