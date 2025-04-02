import re
import asyncio
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam, InputReportReasonFake, InputReportReasonViolence,
    InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonCopyright,
    InputReportReasonIllegalDrugs, InputReportReasonPersonalDetails, InputReportReasonOther
)
from config import SESSION_FILES, ADMINS

# Dictionary for readable report reasons
REPORT_REASONS = {
    "spam": InputReportReasonSpam(),
    "fake": InputReportReasonFake(),
    "violence": InputReportReasonViolence(),
    "pornography": InputReportReasonPornography(),
    "child_abuse": InputReportReasonChildAbuse(),
    "copyright": InputReportReasonCopyright(),
    "illegal_drugs": InputReportReasonIllegalDrugs(),
    "personal_details": InputReportReasonPersonalDetails(),
    "other": InputReportReasonOther(),
}

# Function to validate a Telegram post link
def is_valid_telegram_link(link):
    return re.match(r"https://t\.me/[^/]+/\d+", link)

async def ask_for_link(update, context):
    """Ask user for the group/channel message link."""
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    await update.message.reply_text("📩 Please send the **group/channel message link** you want to report.")
    return "awaiting_link"

async def process_link(update, context):
    """Process the link and show report options."""
    user_id = update.effective_user.id
    text = update.message.text

    if not is_valid_telegram_link(text):
        await update.message.reply_text("❌ Invalid link! Please send a **valid Telegram message link**.")
        return

    context.user_data["report_link"] = text  # Store link
    keyboard = [
        [InlineKeyboardButton("🛑 Spam", callback_data="report_spam")],
        [InlineKeyboardButton("🎭 Fake", callback_data="report_fake")],
        [InlineKeyboardButton("🔪 Violence", callback_data="report_violence")],
        [InlineKeyboardButton("🔞 Pornography", callback_data="report_pornography")],
        [InlineKeyboardButton("👶 Child Abuse", callback_data="report_child_abuse")],
        [InlineKeyboardButton("📜 Copyright", callback_data="report_copyright")],
        [InlineKeyboardButton("💊 Illegal Drugs", callback_data="report_illegal_drugs")],
        [InlineKeyboardButton("🆔 Personal Details", callback_data="report_personal_details")],
        [InlineKeyboardButton("❓ Other", callback_data="report_other")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚠️ **Choose the reason for reporting:**", reply_markup=reply_markup)

async def select_reason(update, context):
    """Store the selected report reason and ask for extra comment."""
    query = update.callback_query
    reason_key = query.data.replace("report_", "")

    context.user_data["report_reason"] = REPORT_REASONS[reason_key]  # Store reason
    await query.answer()
    await query.message.edit_text("✏️ **Provide additional comment for the report (optional):**")

    return "awaiting_comment"

async def process_comment(update, context):
    """Store comment and ask for the number of reports."""
    context.user_data["report_comment"] = update.message.text
    await update.message.reply_text("🔢 **How many reports do you want to submit?** (Enter a number)")

    return "awaiting_report_count"

async def process_report_count(update, context):
    """Start sending reports based on user input."""
    user_id = update.effective_user.id
    try:
        report_count = int(update.message.text)
        if report_count <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid number! Please enter a valid number of reports.")
        return

    context.user_data["report_count"] = report_count
    await update.message.reply_text("✅ **Starting the reporting process...**")

    link = context.user_data["report_link"]
    reason = context.user_data["report_reason"]
    comment = context.user_data["report_comment"]

    successful_reports = 0
    available_sessions = SESSION_FILES

    for session_file in available_sessions:
        if successful_reports >= report_count:
            break

        try:
            async with TelegramClient(session_file, config.API_ID, config.API_HASH) as client:
                await client.connect()
                await asyncio.sleep(0.5)  # Delay between reports
                await client(ReportPeerRequest(link, reason, comment))
                successful_reports += 1

                await update.message.reply_text(f"📊 Reports Sent: {successful_reports}/{report_count}")

        except FloodWaitError as e:
            await update.message.reply_text(f"⏳ Rate limited! Waiting {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error reporting: {e}")

    await update.message.reply_text(f"✅ **Reporting completed!**\n📌 **Total Reports Sent:** {successful_reports}")
