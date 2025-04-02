from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_SESSIONS

async def check_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the number of accounts logged in for an admin."""
    user_id = update.effective_user.id

    admin_accounts = len(ADMIN_SESSIONS.get(user_id, []))
    total_accounts = sum(len(sessions) for sessions in ADMIN_SESSIONS.values())

    message = f"📊 **Your Accounts:** {admin_accounts}\n"
    message += f"🌍 **Total Bot Accounts:** {total_accounts}"

    await update.callback_query.answer()
    await update.callback_query.message.reply_text(message)
