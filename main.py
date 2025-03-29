import os
import subprocess
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

# Pyrogram client setup
bot = Client(
    "FileConverterBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["file_converter"]
users_collection = db["users"]
stats_collection = db["stats"]

# Directories
DOWNLOAD_LOCATION = "./DOWNLOADS"
CONVERTED_PATH = "./CONVERTED"

# Ensure directories exist
os.makedirs(DOWNLOAD_LOCATION, exist_ok=True)
os.makedirs(CONVERTED_PATH, exist_ok=True)

# FFmpeg path check
FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"

def log(msg):
    print(f"🔹 {msg}")

async def update_stats():
    await stats_collection.update_one({"_id": "conversion_stats"}, {"$inc": {"total_conversions": 1}}, upsert=True)

@bot.on_message(filters.command("convertfiletomedia"))
async def convert_file_to_media(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("Please reply to a file to convert it to media.")
        return

    file = message.reply_to_message.document
    file_path = os.path.join(DOWNLOAD_LOCATION, file.file_name)

    log(f"Downloading file: {file.file_name}")
    await message.reply("📥 Downloading file...")

    try:
        downloaded = await client.download_media(file, file_path)
        if not os.path.exists(downloaded):
            log("❌ File download failed!")
            await message.reply("❌ File download failed.")
            return
        log(f"✅ File downloaded: {downloaded}")
    except Exception as e:
        log(f"❌ Download error: {e}")
        await message.reply("❌ Error downloading the file.")
        return

    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(file.file_name)[0] + ".mp4")

    log(f"🔄 Converting {file.file_name} to MP4...")
    await message.reply("⏳ Converting file to media...")

    try:
        cmd = [FFMPEG_PATH, "-i", downloaded, "-c:v", "libx264", output_file]
        subprocess.run(cmd, check=True)
        if not os.path.exists(output_file):
            log("❌ Conversion failed!")
            await message.reply("❌ Conversion failed.")
            return
        log(f"✅ Conversion successful: {output_file}")
        await update_stats()
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg error: {e}")
        await message.reply("❌ FFmpeg conversion error.")
        return

    await message.reply("📤 Uploading media...")
    await message.reply_video(output_file, caption="Here is your converted media!")

@bot.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    stats = await stats_collection.find_one({"_id": "conversion_stats"})
    total_conversions = stats.get("total_conversions", 0) if stats else 0
    await message.reply(f"📊 Total Conversions: {total_conversions}")

from flask import Flask
import threading

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# Start Flask in a separate thread
threading.Thread(target=run_flask, daemon=True).start()

log("🚀 Bot is starting...")
bot.run()
