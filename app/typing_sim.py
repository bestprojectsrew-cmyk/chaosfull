"""
typing_sim.py — Simulates human-like typing delay before sending
"""
import asyncio
import random


async def simulate_typing(
    context,
    chat_id: int,
    reply_length: int,
) -> None:
    """
    Send typing action and wait a human-like amount of time
    based on message length and random variation.
    """
    from telegram.constants import ChatAction

    # Base delay: roughly 30ms per character, capped at 4s
    base_delay = min(len(str(reply_length)) * 0.03, 4.0)

    # Random variation: sometimes fast, sometimes slow, like a real person
    variation = random.choice([
        0.3,   # very fast (pre-typed in head)
        0.6,   # normal
        1.0,   # thinking a bit
        1.5,   # actually thinking
        2.0,   # longer thought
    ])

    total_delay = base_delay + variation

    # Send typing indicator
    await context.bot.send_chat_action(
        chat_id=chat_id,
        action=ChatAction.TYPING,
    )

    # Wait
    await asyncio.sleep(total_delay)

    # For longer replies, send another typing burst
    if reply_length > 200:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.TYPING,
        )
        await asyncio.sleep(random.uniform(0.3, 1.0))
