import logging
import httpx
import nest_asyncio
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# ================= CONFIG (আপনার তথ্য এখানে বসানো হয়েছে) =================
TELEGRAM_TOKEN = "8535188730:AAFxl7kqLD2Bxben8pgAB8ddIauJHHtqddk"
SMS_API_KEY = "$2y$10$8cKMTQTz6E0hdmbghuOjS.NLPWxolWv99uTlHoLC5VCXWq//Wk1D277"
CHANNEL_USERNAME = "@smsbyshourov" # আপনার চ্যানেলের ইউজারনেম
ADMIN_ID = 123456789              # এখানে আপনার নিজের টেলিগ্রাম আইডি দিন (idbot থেকে পাবেন)

SMS_API_URL = "http://sms.greenheritageit.com/smsapi"
MASK_NAME = "MultiSports"

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= MEMORY DB =================
users = {}

def init_user(uid):
    if uid not in users:
        users[uid] = {"balance": 10} # ডিফল্ট ১০ ব্যালেন্স

# ================= FORCE JOIN =================
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, uid)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        pass

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("✅ Verify", callback_data="verify")]
    ])

    await update.message.reply_text(
        f"❌ আগে আমাদের {CHANNEL_USERNAME} চ্যানেলে জয়েন করুন।",
        reply_markup=keyboard
    )
    return False

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, uid)
        if member.status in ["member", "administrator", "creator"]:
            await query.message.edit_text("✅ Verified! এখন /sms কমান্ডটি ব্যবহার করতে পারবেন।")
            return
    except Exception:
        pass
    await query.answer("❌ আপনি এখনো জয়েন করেননি!", show_alert=True)

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)
    await update.message.reply_text(
        "🤖 SMS Bot Ready\n\n"
        "📨 SMS পাঠাতে লিখুন: /sms [নাম্বার] [মেসেজ]\n"
        "💰 ব্যালেন্স দেখতে: /balance"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)
    await update.message.reply_text(f"💰 আপনার বর্তমান ব্যালেন্স: {users[uid]['balance']} টি।")

async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)

    if not await force_join(update, context):
        return

    if users[uid]["balance"] <= 0:
        await update.message.reply_text("❌ আপনার ব্যালেন্স শেষ! দয়া করে অ্যাডমিনের সাথে যোগাযোগ করুন।")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("সঠিক নিয়ম:\n/sms 017XXXXXXXX Hello")
        return

    number = args[0]
    message = " ".join(args[1:])

    payload = {
        "apiKey": SMS_API_KEY,
        "maskName": MASK_NAME,
        "transactionType": "TransactionType",
        "mobileNo": number,
        "message": message
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SMS_API_URL, data=payload, timeout=15.0)
            
        if response.status_code == 200:
            users[uid]["balance"] -= 1
            await update.message.reply_text(f"✅ SMS সফলভাবে পাঠানো হয়েছে।\n📱 নাম্বার: {number}\n💰 বাকি ব্যালেন্স: {users[uid]['balance']}")
        else:
            await update.message.reply_text(f"❌ API সমস্যা। স্ট্যাটাস কোড: {response.status_code}")
    except Exception as e:
        logging.error(f"SMS Error: {e}")
        await update.message.reply_text("❌ সার্ভার সমস্যার কারণে SMS পাঠানো যায়নি।")

async def addbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_uid = int(context.args[0])
        amt = int(context.args[1])
        init_user(target_uid)
        users[target_uid]["balance"] += amt
        await update.message.reply_text(f"✅ ইউজার {target_uid}-কে {amt} ব্যালেন্স দেওয়া হয়েছে।")
    except:
        await update.message.reply_text("নিয়ম: /addbalance [user_id] [amount]")

# ================= MAIN =================
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("sms", sms))
    app.add_handler(CommandHandler("addbalance", addbalance))
    app.add_handler(CallbackQueryHandler(verify, pattern="verify"))

    print("Shourov's SMS Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
