from telegram.constants import ParseMode
from app.owner import is_owner
from app.database import AsyncSessionLocal
from app.crud import get_all_groups, get_all_users


async def cmd_announcegroups(update, context):
    if not is_owner(update.effective_user.id):
        return

    text = update.message.text.replace("/announcegroups", "", 1).strip()

    if not text:
        await update.message.reply_text(
            "Usage:\n/announcegroups your message"
        )
        return

    sent = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        groups = await get_all_groups(db)

    for group in groups:
        try:
            await context.bot.send_message(
                chat_id=group.chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Done!\n\nSent: {sent}\nFailed: {failed}"
    )


async def cmd_announceusers(update, context):
    if not is_owner(update.effective_user.id):
        return

    text = update.message.text.replace("/announceusers", "", 1).strip()

    if not text:
        await update.message.reply_text(
            "Usage:\n/announceusers your message"
        )
        return

    sent = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        users = await get_all_users(db)

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Done!\n\nSent: {sent}\nFailed: {failed}"
    )