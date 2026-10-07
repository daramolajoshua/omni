import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g., @YourChannelName or -100xxxxxxxxxx

async def generate_sports_digest() -> str:
    """Generates the automated sports update text."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"⚽ **OmniSportBot Live Update** — `{now}`\n\n"
        f"🔥 **Hot Matches Today:**\n"
        f"• Real Madrid vs. Barcelona (Live: 2-1, 78')\n"
        f"• Man City vs. Arsenal (Upcoming: 20:00 UTC)\n"
        f"• Lakers vs. Warriors (Final: 112-108)\n\n"
        f"📊 *Use /schedule to view full fixtures or /stats for head-to-head records.*"
    )

async def post_to_channel(context: ContextTypes.DEFAULT_TYPE):
    """Sends the 30-minute automated digest to the channel."""
    try:
        if not CHANNEL_ID:
            logger.warning("CHANNEL_ID is not set in environment variables.")
            return
        
        message = await generate_sports_digest()
        await context.bot.send_message(
            chat_id=CHANNEL_ID, 
            text=message, 
            parse_mode="Markdown"
        )
        logger.info("Successfully posted scheduled update to channel.")
    except Exception as e:
        logger.error(f"Error posting to channel: {e}")

async def post_on_startup(application: Application):
    """Triggers an immediate post right after the bot deploys and starts."""
    logger.info("Bot deployed! Sending immediate startup post...")
    try:
        if CHANNEL_ID:
            startup_msg = "🚀 **OmniSportBot is online and live!** Automated real-time tracking is now active.\n\n" + await generate_sports_digest()
            await application.bot.send_message(
                chat_id=CHANNEL_ID,
                text=startup_msg,
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error sending startup post: {e}")

# Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to **OmniSportBot**!\n\n"
        "Commands:\n"
        "/schedule - View today's fixtures\n"
        "/today - Live scores & tickers\n"
        "/stats - Head-to-head insights",
        parse_mode="Markdown"
    )

async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 **Upcoming Fixtures:**\n- Premier League: 4 matches today\n- NBA: 3 games tonight", parse_mode="Markdown")

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    digest = await generate_sports_digest()
    await update.message.reply_text(digest, parse_mode="Markdown")

def main():
    if not BOT_TOKEN:
        raise ValueError("No BOT_TOKEN provided in environment variables.")

    # Build application
    application = Application.builder().token(BOT_TOKEN).post_init(post_on_startup).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("today", today_command))

    # Configure JobQueue for every 30 minutes interval (1800 seconds)
    job_queue = application.job_queue
    job_queue.run_repeating(post_to_channel, interval=1800, first=10) # first run 10s after boot

    # Start the Bot
    logger.info("Starting OmniSportBot polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
