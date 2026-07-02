"""
moderation/notes.py — Group notes system.

/savenote <name> <content> — save a note
/getnote <name>            — retrieve a note (also: #name)
/delnote <name>            — delete a note (admins only)
/notes                     — list all notes
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from app.database import AsyncSessionLocal
from app.crud import save_note, get_note, delete_note, list_notes

logger = logging.getLogger(__name__)


async def _is_admin(update: Update, context) -> bool:
    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        return member.status in ("administrator", "creator")
    except Exception:
        return False


async def cmd_savenote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("usage: /savenote <name> <content>")
        return

    name = context.args[0].lower()
    content = " ".join(context.args[1:])

    async with AsyncSessionLocal() as db:
        await save_note(db, update.effective_chat.id, name, content, update.effective_user.id)

    await update.message.reply_text(f"✅ note '{name}' saved")


async def cmd_getnote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("usage: /getnote <name>")
        return

    name = context.args[0].lower()
    async with AsyncSessionLocal() as db:
        note = await get_note(db, update.effective_chat.id, name)

    if not note:
        await update.message.reply_text(f"no note found with name '{name}'")
        return

    await update.message.reply_text(note.content)


async def cmd_delnote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only")
        return

    if not context.args:
        await update.message.reply_text("usage: /delnote <name>")
        return

    name = context.args[0].lower()
    async with AsyncSessionLocal() as db:
        deleted = await delete_note(db, update.effective_chat.id, name)

    if deleted:
        await update.message.reply_text(f"✅ note '{name}' deleted")
    else:
        await update.message.reply_text(f"no note found with name '{name}'")


async def cmd_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncSessionLocal() as db:
        notes = await list_notes(db, update.effective_chat.id)

    if not notes:
        await update.message.reply_text("no notes saved for this group")
        return

    names = [f"• #{n.name}" for n in notes]
    await update.message.reply_text(
        "saved notes:\n\n" + "\n".join(names) +
        "\n\nuse /getnote <name> or type #name to get one"
    )


async def handle_hashtag_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Handle #notename shortcut in group messages.
    Returns True if handled.
    """
    if not update.message or not update.message.text:
        return False

    text = update.message.text.strip()
    if not text.startswith("#") or len(text) < 2:
        return False

    name = text[1:].split()[0].lower()
    if not name:
        return False

    async with AsyncSessionLocal() as db:
        note = await get_note(db, update.effective_chat.id, name)

    if note:
        await update.message.reply_text(note.content)
        return True

    return False
