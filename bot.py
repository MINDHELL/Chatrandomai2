import random
import logging
import threading
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, CHANNEL_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from health_check import start_health_check

# Load Environment Variables


API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Initialize bot & database
bot = Client("video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo = MongoClient(MONGO_URL)
db = mongo["VideoBot"]
collection = db["videos"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch and send a random video
async def send_random_video(client, chat_id):
    video_docs = list(collection.find())
    if not video_docs:
        await client.send_message(chat_id, "No videos available. Please index videos first.")
        return

    random_video = random.choice(video_docs)
    await client.forward_messages(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_ids=random_video["message_id"])

# Start command with inline button
@bot.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Get Random Video", callback_data="get_random_video")]
    ])
    await message.reply_text("Welcome! Click the button below to get a random video.", reply_markup=keyboard)

# Command to get a random video
@bot.on_message(filters.command("random"))
async def random_video_command(client, message):
    await send_random_video(client, message.chat.id)

# Callback handler for inline button
@bot.on_callback_query(filters.regex("get_random_video"))
async def random_video_callback(client, callback_query: CallbackQuery):
    await send_random_video(client, callback_query.message.chat.id)
    await callback_query.answer()  # Acknowledge the callback to prevent loading state

if __name__ == "__main__":
    # Run health check in a separate thread
    threading.Thread(target=start_health_check, daemon=True).start()
    
    bot.run()
