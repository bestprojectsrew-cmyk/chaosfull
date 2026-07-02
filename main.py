"""
main.py — FastAPI entry point with Telegram webhook + startup
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from telegram import Update

from app.database import init_db
from app.bot import build_application, set_bot_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

WEBHOOK_URL  = os.getenv("WEBHOOK_URL", "")
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

ptb_app = build_application()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing DB...")
    await init_db()
    logger.info("DB ready ✓")

    await ptb_app.initialize()
    await set_bot_commands(ptb_app)

    webhook_full = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    await ptb_app.bot.set_webhook(
        url=webhook_full,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )
    logger.info(f"Webhook set: {webhook_full} ✓")

    await ptb_app.start()
    logger.info("CHAOS bot v2 is LIVE 🔥")
    yield

    logger.info("Shutting down...")
    await ptb_app.stop()
    await ptb_app.shutdown()


app = FastAPI(title="CHAOS Bot v2", lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data  = await request.json()
        update = Update.de_json(data, ptb_app.bot)
        await ptb_app.process_update(update)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
    return Response(status_code=200)


@app.get("/")
async def root():
    return {"status": "alive", "bot": "CHAOS v2", "vibe": "immaculate 🔥"}


@app.get("/health")
async def health():
    return {"ok": True}
