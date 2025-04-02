import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import InputMediaUploadedPhoto
from config import SESSION_FILES, ADMINS

# Target accounts to report bot/user
TARGET_ACCOUNTS = ["nexaq", "angraaj", "AbuseNotifications"]

async def ask_for_proof(update, context):
    """Ask user for proof (text, media, or both)."""
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    await update.message.reply_text("📌 **Please provide proof (screenshot, text, or both) for the bot/user report.**")
    return "awaiting_proof"

async def process_proof(update, context):
    """Process proof and start sending reports."""
    user = update.effective_user
    message = update.message

    # Store proof (media or text)
    context.user_data["proof"] = message

    await update.message.reply_text("✅ **Proof received!**\n📤 Sending reports now...")

    successful_reports = 0
    available_sessions = SESSION_FILES

    for session_file in available_sessions:
        try:
            async with TelegramClient(session_file, config.API_ID, config.API_HASH) as client:
                await client.connect()

                # Send proof to each target account
                for target in TARGET_ACCOUNTS:
                    if message.photo:
                        # If proof is an image
                        file = await client.upload_file(await message.photo.get_file())
                        media = InputMediaUploadedPhoto(file)
                        await client(SendMediaRequest(target, media, message.caption or "🚨 Report Proof"))
                    else:
                        # If proof is text only
                        await client(SendMessageRequest(target, message.text or "🚨 Report Proof"))

                successful_reports += 1
                await update.message.reply_text(f"📊 Reports Sent: {successful_reports}/{len(available_sessions)}")
                await asyncio.sleep(0.5)  # Delay between reports

        except Exception as e:
            print(f"Error sending report: {e}")

    await update.message.reply_text(f"✅ **Reporting completed!**\n📌 **Total Reports Sent:** {successful_reports}")
