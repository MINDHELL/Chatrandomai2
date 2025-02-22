import random
import logging
import threading
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, CHANNEL_ID
from health_check import start_health_check  # ✅ Import the TCP health check fix

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
        await client.send_message(chat_id, "No videos available. Use /index first!")
        return

    random_video = random.choice(video_docs)
    await client.forward_messages(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_ids=random_video["message_id"])

# Command to manually index videos
@bot.on_message(filters.command("index"))
async def index_videos(client, message):
    if message.chat.type != "private":
        return  # Prevents indexing from group chats

    await message.reply_text("🔄 Indexing videos... This may take a while.")
    
    indexed_count = 0
    async for msg in client.get_chat_history(CHANNEL_ID, limit=1000):
        if msg.video:
            collection.update_one(
                {"message_id": msg.message_id},
                {"$set": {"message_id": msg.message_id}},
                upsert=True
            )
            indexed_count += 1

    await message.reply_text(f"✅ Indexing completed! {indexed_count} videos added.")

# Start command with inline button
@bot.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Get Random Video", callback_data="get_random_video")],
        [InlineKeyboardButton("🔄 Index Videos", callback_data="index_videos")]  # Inline button for indexing
    ])
    await message.reply_text("Welcome! Use the buttons below:", reply_markup=keyboard)

# Callback for random video
@bot.on_callback_query(filters.regex("get_random_video"))
async def random_video_callback(client, callback_query: CallbackQuery):
    await send_random_video(client, callback_query.message.chat.id)
    await callback_query.answer()

# Callback for indexing videos
@bot.on_callback_query(filters.regex("index_videos"))
async def index_videos_callback(client, callback_query: CallbackQuery):
    await index_videos(client, callback_query.message)
    await callback_query.answer()

if __name__ == "__main__":
    threading.Thread(target=start_health_check, daemon=True).start()  # ✅ Start health check
    bot.run()
