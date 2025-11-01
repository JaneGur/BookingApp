import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from supabase import create_client
from app.config.settings import config

app = FastAPI(title="Telegram Bot Webhook")

supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY) if config.SUPABASE_URL and config.SUPABASE_KEY else None
BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        message = update.get("message") or update.get("edited_message") or {}
        text = message.get("text", "")
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))

        if not chat_id:
            return JSONResponse({"ok": True})

        # Deep link: /start connect_<code>
        if text.startswith("/start") and "connect_" in text:
            code = text.split("connect_", 1)[1].strip()
            if supabase and code:
                # Найти phone_hash, начинающийся с кода
                resp = supabase.table('bookings') \
                    .select('phone_hash') \
                    .like('phone_hash', f'{code}%') \
                    .limit(1) \
                    .execute()
                if resp.data:
                    phone_hash = resp.data[0]['phone_hash']
                    # Обновить все записи клиента с этим phone_hash, сохранить chat_id
                    supabase.table('bookings') \
                        .update({'telegram_chat_id': chat_id}) \
                        .eq('phone_hash', phone_hash) \
                        .execute()

                    # Подтверждение пользователю
                    try:
                        requests.post(
                            f"{API_URL}/sendMessage",
                            json={
                                'chat_id': chat_id,
                                'text': '✅ Уведомления подключены! Вы будете получать напоминания и подтверждения.'
                            }, timeout=10
                        )
                    except Exception:
                        pass
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=200)

@app.get("/telegram/set_webhook")
async def set_webhook(webhook_url: str):
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN not configured"}
    resp = requests.get(f"{API_URL}/setWebhook", params={"url": webhook_url}, timeout=10)
    return resp.json()

@app.get("/telegram/delete_webhook")
async def delete_webhook():
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN not configured"}
    resp = requests.get(f"{API_URL}/deleteWebhook", timeout=10)
    return resp.json()
