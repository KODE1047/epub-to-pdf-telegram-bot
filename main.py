# main.py
import logging
import os
import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

import config
import converter

# --- Setup Logging ---
# A basic logging configuration to see bot activity and errors in the console.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
# Set higher logging level for httpx to avoid spam
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.effective_user.first_name
    await update.message.reply_html(
        f"Hello, {user_name}! 👋\n\n"
        f"Send me an EPUB (.epub) file and I will convert it to a PDF for you.\n\n"
        f"<b>Note for Standard Users:</b> File size is limited to {config.MAX_FILE_SIZE_MB} MB."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles file uploads, validates them, and triggers conversion."""
    document = update.message.document
    user_id = update.effective_user.id
    
    # 1. --- File Type Validation ---
    if not document.file_name or not document.file_name.lower().endswith(".epub"):
        await update.message.reply_text("❌ Please send a valid EPUB (.epub) file.")
        return

    # 2. --- File Size Validation ---
    is_admin = user_id in config.ADMIN_IDS
    if not is_admin and document.file_size > config.MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(
            f"❌ File is too large ({document.file_size / 1024 / 1024:.2f} MB). "
            f"The maximum size for standard users is {config.MAX_FILE_SIZE_MB} MB."
        )
        return

    # 3. --- Conversion Process ---
    status_message = await update.message.reply_text("📥 Downloading and processing your file... Please wait.")
    
    epub_path = ""
    pdf_path = ""
    try:
        # Download the file from Telegram
        file = await context.bot.get_file(document.file_id)
        epub_path = os.path.join("temp", f"{document.file_id}.epub")
        os.makedirs("temp", exist_ok=True)
        await file.download_to_drive(epub_path)
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_message.message_id,
            text="⚙️ Converting EPUB to PDF... This might take a moment."
        )
        
        # Call the converter
        pdf_path = await converter.convert_epub_to_pdf(epub_path)
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_message.message_id,
            text="✅ Conversion successful! Uploading your PDF..."
        )
        
        # Send the converted PDF back to the user
        await update.message.reply_document(
            document=pdf_path,
            caption=f"Converted: {os.path.basename(pdf_path)}"
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=status_message.message_id
        )

    except Exception as e:
        logger.error(f"Failed to convert file for user {user_id}: {e}", exc_info=True)
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_message.message_id,
            text=f"❌ An error occurred during conversion: \n`{str(e)}`",
            parse_mode=ParseMode.MARKDOWN
        )
    finally:
        # 4. --- Cleanup ---
        # Ensure temporary files are deleted regardless of success or failure
        if os.path.exists(epub_path):
            os.remove(epub_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def main() -> None:
    """Starts the bot and sets up handlers."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add message handler for documents
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Bot is starting...")
    # Start polling for updates
    application.run_polling()


if __name__ == "__main__":
    main()