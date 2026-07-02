# CHAOS Bot 🔥
> Gen Z AI Telegram bot — raw, chaotic, multilingual, zero filter

Built with: FastAPI · python-telegram-bot · Groq (Llama 3) · PostgreSQL on Railway

---

## Stack (100% free tier)

| Layer | Service | Cost |
|---|---|---|
| Bot framework | python-telegram-bot 21 | free |
| LLM | Groq — Llama 3.1 70B | free (rate limited) |
| Backend | FastAPI + uvicorn | free |
| Database | PostgreSQL on Railway | free (500MB) |
| Hosting | Railway | free ($5 credit/month) |
| Language detection | langdetect (local) | free |

---

## Features

- **Gen Z personality** — slang, cursing, real talk, no corporate filter
- **Auto language detection** — Uzbek, Russian, English, Turkish, Arabic, and 15+ more
- **Conversation memory** — last 12 messages stored in PostgreSQL
- **Commands:** `/start`, `/help`, `/clear`, `/stats`
- **Group chat support** — responds when mentioned or replied to
- **Webhook mode** — no polling, production-ready

---

## Setup Guide

### Step 1 — Get your API keys

**Telegram Bot Token:**
1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow the steps, copy the token

**Groq API Key (free):**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free, no card needed)
3. Go to API Keys → Create API Key
4. Copy it

---

### Step 2 — Deploy PostgreSQL on Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Database** → **PostgreSQL**
3. Wait for it to provision
4. Click on the PostgreSQL service → **Variables** tab
5. Copy the `DATABASE_URL` value (starts with `postgresql://...`)

---

### Step 3 — Deploy the bot on Railway

1. Push this project to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "chaos bot init"
   git remote add origin https://github.com/YOURUSERNAME/chaos-bot.git
   git push -u origin main
   ```

2. In Railway: **New Project** → **Deploy from GitHub repo**
3. Select your repo
4. Railway will auto-detect Python and build it

5. Go to your service → **Variables** tab → Add these:
   ```
   TELEGRAM_BOT_TOKEN   = your_telegram_bot_token
   GROQ_API_KEY         = your_groq_api_key
   DATABASE_URL         = postgresql://... (from step 2)
   WEBHOOK_URL          = (leave empty for now)
   ```

6. Go to **Settings** → **Networking** → **Generate Domain**
7. Copy the generated URL (like `https://chaos-bot-production.up.railway.app`)
8. Go back to **Variables** → set `WEBHOOK_URL` to that URL

9. **Redeploy** the service (click the three dots → Redeploy)

That's it. Railway handles the rest.

---

### Step 4 — Test it

Open Telegram, find your bot, send `/start`. It should reply immediately.

Try sending in different languages:
- English: `yo what's the capital of france`
- Russian: `как дела братан`
- Uzbek: `salom bro nima yangilik`

---

## Local Development

```bash
# Clone and install
git clone https://github.com/YOURUSERNAME/chaos-bot.git
cd chaos-bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy env and fill it in
cp .env.example .env
# Edit .env with your keys

# For local dev, you need a public URL for the webhook.
# Use ngrok: ngrok http 8000
# Then set WEBHOOK_URL=https://your-ngrok-url.ngrok.io in .env

# Run
uvicorn main:app --reload --port 8000
```

---

## Project Structure

```
chaos-bot/
├── main.py              # FastAPI app + webhook endpoint
├── app/
│   ├── __init__.py
│   ├── bot.py           # Telegram handlers (commands + messages)
│   ├── llm.py           # Groq client + system prompt
│   ├── database.py      # SQLAlchemy models + async engine
│   ├── crud.py          # DB read/write operations
│   └── language.py      # Language detection utility
├── requirements.txt
├── Procfile
├── railway.toml
├── .env.example
└── .gitignore
```

---

## Customizing the Personality

Edit `app/llm.py` → `BASE_SYSTEM_PROMPT`.

Change the slang, energy level, cursing frequency, or add domain-specific knowledge. The prompt is designed to be modular — just add more rules.

To change the LLM model, edit `MODEL` in `app/llm.py`. Available free Groq models:
- `llama-3.1-70b-versatile` — best quality (default)
- `llama-3.1-8b-instant` — faster, lighter
- `mixtral-8x7b-32768` — good for long context

---

## Groq Free Tier Limits

- ~30 requests/minute
- ~14,400 tokens/minute
- Resets every minute

For a personal bot this is more than enough. If you hit limits, the bot responds with a friendly retry message.

---

## Common Issues

**Bot not responding:**
- Check Railway logs for errors
- Verify `WEBHOOK_URL` matches your Railway domain exactly (no trailing slash)
- Make sure `DATABASE_URL` is set correctly

**Database connection errors:**
- Railway's PostgreSQL URL uses `postgres://` — the app auto-converts it to `postgresql+asyncpg://`
- If it still fails, check if the PostgreSQL service is running in Railway

**LangDetect errors on short messages:**
- Short messages (1-2 words) sometimes fail detection → falls back to English
- This is expected behavior

---

## License

Do whatever you want with it. It's free. No cap.
