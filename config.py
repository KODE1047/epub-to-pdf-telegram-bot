# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Telegram Bot Configuration ---
# Retrieve the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the .env file.")

# --- User Tier Configuration ---
# Retrieve and parse the list of admin user IDs
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
try:
    # Convert the comma-separated string of IDs into a set of integers for efficient lookup
    ADMIN_IDS = {int(admin_id) for admin_id in ADMIN_IDS_STR.split(',') if admin_id}
except ValueError:
    raise ValueError("ADMIN_IDS in .env file contains non-integer values.")

# --- File Size Configuration ---
# Maximum file size for standard users in megabytes
MAX_FILE_SIZE_MB = 10
# Convert megabytes to bytes for comparison with file metadata
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024