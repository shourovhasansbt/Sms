‎import requests
‎import nest_asyncio
‎import asyncio
‎import time
‎
‎from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
‎from telegram.ext import (
‎    ApplicationBuilder,
‎    ContextTypes,
‎    CommandHandler,
‎    CallbackQueryHandler,
‎)
‎
‎# ================= CONFIG =================
‎TELEGRAM_TOKEN = "8535188730:AAFxl7kqLD2Bxben8pgAB8ddIauJHHtqddk"
‎ADMIN_ID = 123456789        # your telegram id
‎CHANNEL_USERNAME = "@smsbyshourov"
‎
‎SMS_API_URL = "http://sms.greenheritageit.com/smsapi"
‎SMS_API_KEY = "$2y$10$8cKMTQTz6E0hdmbghuOjS.NLPWxolWv99uTlHoLC5VCXWq//Wk1D277"
‎MASK_NAME = "MultiSports"
‎
‎# ================= MEMORY DB =================
‎users = {}
‎
‎def init_user(uid):
‎    if uid not in users:
‎        users[uid] = {
‎            "balance": 10   # default balance
‎        }
‎
‎# ================= FORCE JOIN =================
‎async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    uid = update.effective_user.id
‎    try:
‎        member = await context.bot.get_chat_member(CHANNEL_USERNAME, uid)
‎        if member.status in ["member", "administrator", "creator"]:
‎            return True
‎    except:
‎        pass
‎
‎    keyboard = InlineKeyboardMarkup([
‎        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
‎        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
‎    ])
‎
‎    await update.message.reply_text(
‎        "❌ আগে channel join করো",
‎        reply_markup=keyboard
‎    )
‎    return False
‎
‎async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    query = update.callback_query
‎    await query.answer()
‎
‎    uid = query.from_user.id
‎    try:
‎        member = await context.bot.get_chat_member(CHANNEL_USERNAME, uid)
‎        if member.status in ["member", "administrator", "creator"]:
‎            await query.message.edit_text("✅ Verified! এখন /sms use করো")
‎            return
‎    except:
‎        pass
‎
‎    await query.message.edit_text("❌ এখনো join করোনি")
‎
‎# ================= COMMANDS =================
‎async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    uid = update.effective_user.id
‎    init_user(uid)
‎    await update.message.reply_text(
‎        "🤖 SMS Bot Ready\n\n"
‎        "📨 /sms number message\n"
‎        "💰 /balance"
‎    )
‎
‎async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    uid = update.effective_user.id
‎    init_user(uid)
‎    await update.message.reply_text(f"💰 Balance: {users[uid]['balance']}")
‎
‎# ================= SMS (NO DAILY LIMIT) =================
‎async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    uid = update.effective_user.id
‎    init_user(uid)
‎
‎    if not await force_join(update, context):
‎        return
‎
‎    if users[uid]["balance"] <= 0:
‎        await update.message.reply_text("❌ ব্যালেন্স শেষ")
‎        return
‎
‎    args = context.args
‎    if len(args) < 2:
‎        await update.message.reply_text(
‎            "Usage:\n/sms 01XXXXXXXXX message"
‎        )
‎        return
‎
‎    number = args[0]
‎    message = " ".join(args[1:])
‎
‎    payload = {
‎        "apiKey": SMS_API_KEY,
‎        "maskName": MASK_NAME,
‎        "transactionType": "TransactionType",
‎        "mobileNo": number,
‎        "message": message
‎    }
‎
‎    try:
‎        r = requests.post(SMS_API_URL, data=payload, timeout=15)
‎        users[uid]["balance"] -= 1
‎        await update.message.reply_text("✅ SMS পাঠানো হয়েছে")
‎    except Exception as e:
‎        await update.message.reply_text("❌ SMS failed")
‎
‎# ================= ADMIN =================
‎async def addbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
‎    if update.effective_user.id != ADMIN_ID:
‎        return
‎
‎    try:
‎        uid = int(context.args[0])
‎        amt = int(context.args[1])
‎        init_user(uid)
‎        users[uid]["balance"] += amt
‎        await update.message.reply_text("✅ Balance added")
‎    except:
‎        await update.message.reply_text(
‎            "Usage:\n/addbalance user_id amount"
‎        )
‎
‎# ================= MAIN =================
‎async def main():
‎    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
‎
‎    app.add_handler(CommandHandler("start", start))
‎    app.add_handler(CommandHandler("balance", balance))
‎    app.add_handler(CommandHandler("sms", sms))
‎    app.add_handler(CommandHandler("addbalance", addbalance))
‎    app.add_handler(CallbackQueryHandler(verify, pattern="verify"))
‎
‎    print("Bot running...")
‎    await app.run_polling()
‎
‎if __name__ == "__main__":
‎    nest_asyncio.apply()
‎    asyncio.run(main()
