"""
typing_sim.py — Human-like typing delay based on reply length.
"""
import asyncio
import random
from telegram.constants import ChatAction


async def simulate_typing(context, chat_id: int, reply_len: int) -> None:
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    # Short message = fast reply, long = more time
    base = min(reply_len / 400, 3.0)
    jitter = random.uniform(0.2, 0.8)
    await asyncio.sleep(base + jitter)
    # Second burst for longer replies
    if reply_len > 300:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(random.uniform(0.3, 0.7))
