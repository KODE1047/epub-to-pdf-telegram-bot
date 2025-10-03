# Telegram EPUB to PDF Converter Bot

A robust, production-ready Telegram bot that converts EPUB files to PDF format. It features different access tiers for standard and admin users.

## Features

-   **EPUB to PDF Conversion**: Simply send an `.epub` file to the bot.
-   **User Tiers**:
    -   **Standard Users**: File size limit of 10 MB.
    -   **Admin Users**: No file size limitations.
-   **Asynchronous**: Built with `asyncio` and `python-telegram-bot` v20+ to handle multiple users efficiently.
-   **Error Handling**: Provides clear feedback to users for invalid files, oversized files, or conversion failures.
-   **Secure Configuration**: Uses a `.env` file to keep your bot token and admin list private.

## Project Structure

```
epub-to-pdf-bot/
├── .env              # Stores configuration variables
├── config.py         # Loads and parses environment variables
├── converter.py      # Handles the EPUB to PDF conversion logic
├── main.py           # Main bot application file
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

## Setup and Deployment

Follow these steps to get your bot running.

### 1. Prerequisites

-   Python 3.8 or higher.
-   A Telegram Bot Token from [BotFather](https://t.me/BotFather).
-   Your Telegram User ID (and other admin IDs). You can get this from a bot like [@userinfobot](https://t.me/userinfobot).

### 2. Clone the Repository

Clone this project to your local machine or server.

```bash
git clone <your-repository-url>
cd epub-to-pdf-bot
```

### 3. Install Dependencies

Create a virtual environment (optional but recommended) and install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=your_telegram_user_id,other_admin_ids
```

Replace `your_telegram_bot_token_here` with your actual bot token from BotFather, and `your_telegram_user_id` with your Telegram User ID (you can get this from [@userinfobot](https://t.me/userinfobot)).

### 5. Run the Bot

Start the bot with:

```bash
python main.py
```

Your bot should now be running and ready to convert EPUB files to PDF!

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.