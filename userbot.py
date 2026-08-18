# userbot.py — সোর্স চ্যানেলের পোস্ট পড়ে → পরিষ্কার করে → আপনার চ্যানেলে
import asyncio
from telethon import TelegramClient, events
from telegram.ext import Application

from config import BOT_TOKEN, API_ID, API_HASH, SESSION, PHONE, SOURCE_CHANNELS, DEST_CHANNEL_ID
from privacy import clean_personal

bot_app = Application.builder().token(BOT_TOKEN).build()
user_client = TelegramClient(SESSION, API_ID, API_HASH)

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def on_new_post(event):
    msg = event.message
    text = msg.text or msg.message or ""
    if not text.strip():
        print("📎 মিডিয়া পোস্ট (টেক্সট নেই) — স্কিপ")
        return
    safe = clean_personal(text)                    # 🛡️ personal data মুছে দিল
    if safe:
        await bot_app.bot.send_message(DEST_CHANNEL_ID, safe)
        print(f"✅ পোস্ট হয়েছে → {safe[:50]}...")

async def main():
    await bot_app.initialize()
    await bot_app.start()
    await user_client.start(phone=PHONE)           # প্রথমবার OTP চাইবে
    print(f"👀 {len(SOURCE_CHANNELS)}টা সোর্স চ্যানেল দেখা হচ্ছে...")
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
