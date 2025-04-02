import logging import pytz from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters from apscheduler.schedulers.asyncio import AsyncIOScheduler from datetime import datetime from handlers.login import add_session, verify_sessions from handlers.check_accounts import check_admin_accounts, check_total_accounts

Bot credentials

API_ID = 26510660 API_HASH = "1c5017dbd3cbb417770c19d4a5645fa2" BOT_TOKEN = "7818162640:AAGmIkrkd8kxaglbNFBpXxrP7bAL6c2sEOk" OWNER_ID = 7046757969

Enable logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

Initialize scheduler with explicit timezone

scheduler = AsyncIOScheduler(timezone=pytz.UTC) scheduler.start()

async def start(update: Update, context): user_id = update.effective_user.id if user_id != OWNER_ID: await update.message.reply_text("Access Denied. Only the owner can use this bot.") return

keyboard = [[
    InlineKeyboardButton("Login", callback_data="login"),
    InlineKeyboardButton("Check Accounts", callback_data="check_accounts"),
    InlineKeyboardButton("Report", callback_data="report")
]]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def button_handler(update: Update, context): query = update.callback_query user_id = query.from_user.id await query.answer()

if user_id != OWNER_ID:
    await query.message.edit_text("Access Denied. Only the owner can use this bot.")
    return

if query.data == "login":
    await query.message.edit_text("Send your session details to login.")
elif query.data == "check_accounts":
    admin_count = check_admin_accounts(user_id)
    total_count = check_total_accounts()
    await query.message.edit_text(f"Your accounts: {admin_count}\nTotal accounts: {total_count}")
elif query.data == "report":
    keyboard = [[
        InlineKeyboardButton("Group/Channel", callback_data="report_group_channel"),
        InlineKeyboardButton("Bot/User Account", callback_data="report_bot_user")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Select report type:", reply_markup=reply_markup)

Main function to run the bot

def main(): app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

logger.info("Bot started...")
app.run_polling()

if name == "main": main()

