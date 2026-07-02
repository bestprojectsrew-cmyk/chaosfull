"""
moderation/filters.py — Word/phrase filter system.

Admins set triggers with /filter word response
When a group message contains the trigger, bot responds with:
  - The custom text
  - A GIF (searched via Tenor)
  - A photo
  - Or all of the above
"""

import logging
import httpx
import os
from telegram import Update
from telegram.ext import ContextTypes

from app.database import AsyncSessionLocal
from app.crud import add_filter, remove_filter, get_filters, get_matching_filter

logger = logging.getLogger(__name__)

TENOR_KEY = os.getenv("TENOR_API_KEY", "")  # optional, free at tenor.com


async def _is_admin(update: Update, context) -> bool:
    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id, update.effective_user.id
        )
        return member.status in ("administrator", "creator")
    except Exception:
        return False


async def _fetch_gif(query: str) -> str | None:
    """Fetch a GIF URL from Tenor for the given query."""
    if not TENOR_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://tenor.googleapis.com/v2/search",
                params={"q": query, "key": TENOR_KEY, "limit": 5, "contentfilter": "medium"},
            )
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                import random
                pick = random.choice(results[:5])
                return pick["media_formats"]["gif"]["url"]
    except Exception as e:
        logger.debug(f"Tenor fetch failed: {e}")
    return None


# ── Commands ──────────────────────────────────────────────────────────────────

async def cmd_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /filter <trigger> <response>
    /filter <trigger> (no response = AI generates one)
    """
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only")
        return

    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "usage: /filter <word> <response text>\n"
            "example: /filter england Water bottle 😭\n\n"
            "use /filters to see all active filters\n"
            "use /delfilter <word> to remove one"
        )
        return

    trigger = context.args[0]
    response_text = " ".join(context.args[1:]) if len(context.args) > 1 else None

    async with AsyncSessionLocal() as db:
        await add_filter(
            db,
            chat_id=update.effective_chat.id,
            trigger=trigger,
            response_text=response_text,
            response_type="all",
            created_by=update.effective_user.id,
        )

    await update.message.reply_text(
        f"✅ filter set for '{trigger}'"
        + (f"\nresponse: {response_text}" if response_text else "\nresponse: AI generated")
    )


async def cmd_delfilter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_admin(update, context):
        await update.message.reply_text("admins only")
        return

    if not context.args:
        await update.message.reply_text("usage: /delfilter <word>")
        return

    trigger = context.args[0]
    async with AsyncSessionLocal() as db:
        removed = await remove_filter(db, update.effective_chat.id, trigger)

    if removed:
        await update.message.reply_text(f"✅ filter '{trigger}' removed")
    else:
        await update.message.reply_text(f"no filter found for '{trigger}'")


async def cmd_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncSessionLocal() as db:
        filters = await get_filters(db, update.effective_chat.id)

    if not filters:
        await update.message.reply_text("no filters set for this group")
        return

    lines = ["active filters:\n"]
    for f in filters:
        resp = f.response_text[:40] + "..." if f.response_text and len(f.response_text) > 40 else (f.response_text or "AI generated")
        lines.append(f"• {f.trigger} → {resp}")

    await update.message.reply_text("\n".join(lines))


async def handle_filter_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if message triggers a filter. Send response if so.
    Returns True if a filter was triggered (bot.py skips normal processing).
    """
    if not update.message or not update.message.text:
        return False

    text = update.message.text

    async with AsyncSessionLocal() as db:
        matched = await get_matching_filter(db, update.effective_chat.id, text)

    if not matched:
        return False

    response_text = matched.response_text

    # If no custom text, generate one with AI
    if not response_text:
        try:
            from app import providers
            response_text = await providers.chat(
                messages=[{
                    "role": "user",
                    "content": (
                        f"Someone said '{matched.trigger}' in a group chat. "
                        f"Reply with a short funny reaction (1-2 sentences max, no markdown)."
                    )
                }],
                max_tokens=80,
                temperature=0.9,
                tier="fast",
            )
        except Exception:
            response_text = f"someone said {matched.trigger} 👀"

    # Send text
    await update.message.reply_text(response_text)

    # Send GIF if Tenor configured
    if matched.response_type in ("gif", "all") and TENOR_KEY:
        gif_url = await _fetch_gif(matched.trigger)
        if gif_url:
            try:
                await update.message.reply_animation(gif_url)
            except Exception as e:
                logger.debug(f"GIF send failed: {e}")

    return True
