import logging
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, CHANNEL_ID
from pyrogram import Client
from pymongo import MongoClient

# Load Environmen

bot = Client("indexer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo = MongoClient(MONGO_URL)
db = mongo["VideoBot"]
collection = db["videos"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def index_videos():
    async with bot:
        async for message in bot.get_chat_history(CHANNEL_ID, limit=1000):
            if message.video:
                collection.update_one(
                    {"message_id": message.message_id},
                    {"$set": {"message_id": message.message_id}},
                    upsert=True
                )
        logger.info("Indexing completed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(index_videos())
