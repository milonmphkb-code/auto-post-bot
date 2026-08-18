# main.py — অ্যাডমিন প্যানেল বট (বাংলা, ss-এর মতো বাটন)
from dotenv import load_dotenv
load_dotenv()

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          CallbackQueryHandler, filters, ContextTypes)

from config import BOT_TOKEN, ADMIN_IDS, SOURCE_CHANNELS

def main_kb():
    return ReplyKeyboardMarkup([
        ["GET NUMBER"],
        ["TRAFFIC", "BALANCE"],
        ["REFER & EARN", "MY STATUS"],
        ["SUPPORT"],
        ["ADMIN PANEL"],
    ], resize_keyboard=True)

def admin_kb():
    return ReplyKeyboardMarkup([
        ["🛡️ Security & Join"],
        ["📡 Channel Settings"],
        ["📝 Auto Post"],
        ["📊 Statistics"],
        ["⬅️ BACK TO MAIN"],
    ], resize_keyboard=True)

def security_kb():
    return ReplyKeyboardMarkup([
        ["🔔 Toggle Join Alert"],
        ["⭐ Toggle Force Join"],
        ["⬅️ BACK TO ADMIN"],
    ], resize_keyboard=True)

def channel_kb():
    return ReplyKeyboardMarkup([
        ["🏠 My Channels", "📡 Source Channels"],
        ["🔗 Mapping"],
        ["⬅️ BACK TO ADMIN"],
    ], resize_keyboard=True)

def app_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Facebook", callback_data="app:facebook")],
        [InlineKeyboardButton("WhatsApp", callback_data="app:whatsapp")],
        [InlineKeyboardButton("Discord", callback_data="app:discord")],
    ])

user_state = {}
settings = {"join_alert": True, "force_join": False}
my_channels = {}   # ডেস্টিনেশন চ্যানেল (পরের ফেজে DB)

def is_admin(uid): return uid in ADMIN_IDS

async def start(update, ctx):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ অনুমতি নেই。"); return
    await update.message.reply_text("⭐ WELCOME ADMIN PANEL ⭐", reply_markup=main_kb())

async def app_cb(update, ctx):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id): return
    app = q.data.split(":")[1]
    user_state[q.from_user.id] = {"step": "await_number", "app": app}
    await q.edit_message_text(f"📱 {app.title()} সিলেক্ট হয়েছে!\n\n🔢 এখন আপনার নাম্বার লিখুন:")

async def handle_forward(update, ctx):
    fwd = update.message.forward_from_chat
    state = user_state.get(update.effective_user.id, {})
    if not fwd or state.get("step") != "await_channel_url":
        await update.message.reply_text("💡 আগে '🏠 My Channels' চাপুন, তারপর চ্যানেল থেকে পোস্ট ফরোয়ার্ড করুন。")
        return
    name = fwd.username or str(fwd.id)
    my_channels[name] = {"id": fwd.id, "title": fwd.title or name, "status": "চালু"}
    user_state[update.effective_user.id].pop("step", None)
    await update.message.reply_text(f"✅ চ্যানেল যোগ হয়েছে!\n\n📛 নাম: {fwd.title}\n🆔 ID: {fwd.id}", reply_markup=channel_kb())

async def handle(update, ctx):
    t = update.message.text
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ অনুমতি নেই。"); return

    # ধাপ: GET NUMBER → নাম্বার লেখা
    if uid in user_state and user_state[uid]["step"] == "await_number":
        number = t.strip()
        if not number.replace("+", "").isdigit():
            await update.message.reply_text("⚠️ নাম্বার ঠিক নেই। শুধু সংখ্যা লিখুন:"); return
        app = user_state[uid]["app"]; user_state.pop(uid)
        await update.message.reply_text(f"✅ সফল!\n\n📱 অ্যাপ: {app.title()}\n🔢 নাম্বার: {number}", reply_markup=main_kb())
        return

    # ধাপ: My Channels → URL দিয়ে যোগ
    if uid in user_state and user_state[uid]["step"] == "await_channel_url":
        username = t.replace("https://t.me/", "").replace("@", "").split("/")[0]
        try:
            chat = await ctx.bot.get_chat(f"@{username}")
            my_channels[username] = {"id": chat.id, "title": chat.title or username, "status": "চালু"}
            user_state.pop(uid)
            await update.message.reply_text(f"✅ চ্যানেল যোগ হয়েছে!\n\n📛 নাম: {chat.title}\n🆔 ID: {chat.id}", reply_markup=channel_kb())
        except Exception:
            await update.message.reply_text("❌ চ্যানেল পাওয়া যায়নি। বট অ্যাডমিন আছে তো?")
        return

    if t == "GET NUMBER":
        user_state[uid] = {"step": "select_app"}
        await update.message.reply_text("⭐ SELECT APP TO GET", reply_markup=app_kb())
    elif t == "TRAFFIC":
        await update.message.reply_text("🚦 ট্রাফিক স্ট্যাটাস\n\n✅ মোট: ১,২৩৪\n📊 আজ: ৫৬")
    elif t == "BALANCE":
        await update.message.reply_text("💰 ব্যালেন্স\n\nবর্তমান: ৳০.০০")
    elif t == "REFER & EARN":
        await update.message.reply_text("🎁 REFER & EARN\n\nলিংক: https://t.me/yourbot?start=ref_123")
    elif t == "MY STATUS":
        await update.message.reply_text("📊 MY STATUS\n\n✅ অ্যাক্টিভ")
    elif t == "SUPPORT":
        await update.message.reply_text("🛠️ SUPPORT\n\n@your_support")
    elif t == "ADMIN PANEL":
        await update.message.reply_text("⭐ WELCOME ADMIN PANEL ⭐", reply_markup=admin_kb())
    elif t == "⬅️ BACK TO MAIN":
        await update.message.reply_text("Back to main menu.", reply_markup=main_kb())

    elif t == "🛡️ Security & Join":
        await update.message.reply_text("🛡️ Security & Join ক্যাটাগরি:", reply_markup=security_kb())
    elif t == "🔔 Toggle Join Alert":
        settings["join_alert"] = not settings["join_alert"]
        st = "চালু হয়েছে ✅" if settings["join_alert"] else "বন্ধ হয়েছে ❌"
        await update.message.reply_text(f"⭐ New User Join Notification এখন {st}!", reply_markup=security_kb())
    elif t == "⭐ Toggle Force Join":
        settings["force_join"] = not settings["force_join"]
        st = "চালু হয়েছে ✅" if settings["force_join"] else "বন্ধ হয়েছে ❌"
        await update.message.reply_text(f"⭐ Force Join System এখন {st}!", reply_markup=security_kb())
    elif t == "⬅️ BACK TO ADMIN":
        await update.message.reply_text("Back to admin panel.", reply_markup=admin_kb())

    elif t == "📡 Channel Settings":
        await update.message.reply_text("📡 চ্যানেল সেটিংস:", reply_markup=channel_kb())
    elif t == "🏠 My Channels":
        user_state[uid] = {"step": "await_channel_url"}
        lst = "\n".join(f"🟢 {c['title']}" for c in my_channels.values()) or "খালি"
        await update.message.reply_text(f"🏠 আমার চ্যানেল:\n{lst}\n\n➕ URL পাঠান (t.me/...) বা পোস্ট ফরোয়ার্ড করুন:")
    elif t == "📡 Source Channels":
        lst = "\n".join(f"📡 {s}" for s in SOURCE_CHANNELS) or "খালি — .env-এ SOURCE_CHANNELS বসান"
        await update.message.reply_text(f"📡 সোর্স চ্যানেল:\n{lst}")
    elif t == "🔗 Mapping":
        await update.message.reply_text("🔗 ম্যাপিং\n\n⚠️ ম্যাপিং + ডাটাবেস পরের ধাপে যোগ হবে。")
    elif t == "📝 Auto Post":
        await update.message.reply_text("📝 অটো পোস্ট\n\n✅ userbot চালু আছে? → python userbot.py")
    elif t == "📊 Statistics":
        await update.message.reply_text(f"📊 পরিসংখ্যান\n\n📡 সোর্স: {len(SOURCE_CHANNELS)}\n🏠 ডেস্টিনেশন: {len(my_channels)}")
    else:
        await update.message.reply_text("❌ চিনতে পারিনি। নিচের বাটন ব্যবহার করুন。")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(app_cb, pattern="^app:"))
    app.add_handler(MessageHandler(filters.FORWARDED & filters.ChatType.PRIVATE, handle_forward))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle))
    print("🤖 অ্যাডমিন বট চালু হয়েছে")
    app.run_polling()

if __name__ == "__main__":
    main()
