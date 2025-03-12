import logging
import asyncio
import os  # Import the os module to handle file deletion
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "7602089383:AAH9Hu589_8NUXqhtDG5fsrOCWUxIO9mnlY"
API_ID = 25742525
API_HASH = "a734126107ce3fa3c711a6993a5ebfa1"
PHONE_NUMBER = "+918156935171"
TARGET_BOT = "TeraboxDownloader_4Bot"

# Global trackers
client = TelegramClient("session_name", API_ID, API_HASH)
app = None
pending_requests = {}  # {target_bot_msg_id: user_chat_id}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Welcome to the Auto Link Converter Bot!* 🌟\n\n"
        "🚀 *Powered by Jambucode*\n\n"
        "📌 *How to use:*\n"
        "1. Send any Tera link to convert.\n"
        "2. Sit back and let the bot do the magic!\n\n"
        "🔗 Example: `https://terafileshare.com/s/example`\n\n"
        "Enjoy! 😊"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        original_link = update.message.text
        user_chat_id = update.message.chat_id
        
        if not ("tera" in original_link.lower() and original_link.startswith(("http://", "https://"))):
            await update.message.reply_text("❌ *Invalid link format!*\n\n"
                                          "Please send a valid Tera link. Example: `https://terafileshare.com/s/example`")
            return

        # Convert link
        converted_link = original_link.replace(
            "terafileshare.com/s/", "teraboxlink.com/s/"
        ).replace(
            "terasharelink.com/s/", "teraboxlink.com/s/"
        )

        # Send to target bot and track message
        target_msg = await client.send_message(TARGET_BOT, converted_link)
        pending_requests[target_msg.id] = user_chat_id
        
        logger.info(f"Forwarded link to target bot. Message ID: {target_msg.id}")
        await update.message.reply_text(
            "⏳ *Processing your request...*\n\n"
            "I'll forward the response as soon as it's ready! 🚀",
            disable_web_page_preview=True
        )

    except Exception as e:
        logger.error(f"Message handling error: {str(e)}")
        await update.message.reply_text("⚠️ *An error occurred. Please try again.*")

@client.on(events.NewMessage(chats=TARGET_BOT))
async def handle_target_response(event):
    try:
        response = event.message
        logger.info(f"Received response from target bot (ID: {response.id})")

        # Find original request using reply chain
        if response.is_reply:
            original_msg_id = response.reply_to_msg_id
            if original_msg_id in pending_requests:
                user_chat_id = pending_requests.pop(original_msg_id)
            else:
                logger.warning(f"No pending request found for message ID: {original_msg_id}")
                return
        else:
            logger.warning("Received non-reply message from target bot")
            return

        # Forward media files
        if isinstance(response.media, MessageMediaDocument):
            file = await client.download_media(response.media)
            await app.bot.send_document(
                chat_id=user_chat_id,
                document=open(file, 'rb'),
                caption=f"✅ Your file is ready! Enjoy! 😊"
            )
            logger.info(f"Forwarded document {response.id} to user {user_chat_id}")
            os.remove(file)  # Delete the file from the server after sending

        elif isinstance(response.media, MessageMediaPhoto):
            file = await client.download_media(response.media)
            await app.bot.send_photo(
                chat_id=user_chat_id,
                photo=open(file, 'rb'),
                caption=f"✅ Your photo is ready! Enjoy! 😊"
            )
            logger.info(f"Forwarded photo {response.id} to user {user_chat_id}")
            os.remove(file)  # Delete the file from the server after sending

        # Forward text messages
        elif response.text:
            await app.bot.send_message(
                chat_id=user_chat_id,
                text=f"📬 *Response from @{TARGET_BOT}:*\n\n"
                     f"{response.text}\n\n"
                     "✅ Request completed! 🎉",
                disable_web_page_preview=True
            )
            logger.info(f"Forwarded text response {response.id} to user {user_chat_id}")

    except Exception as e:
        logger.error(f"Response handling error: {str(e)}")

async def main():
    global app
    await client.start(PHONE_NUMBER)
    logger.info("Telethon client initialized")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
