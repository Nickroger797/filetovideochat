import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN
from utils.ffmpeg_util import convert_video
from database import users_col, logs_col

# ✅ Debugging Mode Enable (Logs देखने के लिए)
logging.basicConfig(level=logging.DEBUG)

# ✅ Initialize Bot
bot = Client(
    "video_converter_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ✅ Check MongoDB Connection
try:
    from database import client  # MongoDB Client
    client.server_info()  # Check if MongoDB is connected
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print("❌ MongoDB Connection Error:", e)
    exit(1)  # Bot बंद कर दो अगर database connect नहीं हुआ

# ✅ /start Command
@bot.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    await message.reply_text("👋 Welcome! Send me a video file, and I'll convert it to Telegram's gallery mode.")

# ✅ /stats Command
@bot.on_message(filters.command("stats"))
async def stats_handler(client: Client, message: Message):
    total_users = users_col.count_documents({})
    total_conversions = logs_col.count_documents({})
    await message.reply_text(f"📊 **Bot Stats**:\n👥 Total Users: {total_users}\n🎥 Total Conversions: {total_conversions}")

# ✅ Video Conversion Handler
@bot.on_message(filters.video | filters.document)
async def convert_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not message.video and not message.document:
        await message.reply_text("⚠️ Please send a video file.")
        return

    file_path = await message.download()
    output_path = convert_video(file_path)

    await message.reply_video(video=output_path, caption="✅ Here is your converted video!", supports_streaming=True)
    os.remove(file_path)
    os.remove(output_path)

    logs_col.insert_one({"user_id": user_id, "file": message.document.file_name if message.document else "video", "status": "converted"})

# ✅ Run Bot
if __name__ == "__main__":
    bot.run()
