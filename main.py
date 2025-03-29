import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient

# Pyrogram client setup
bot = Client(
    "FileConverterBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["file_converter_bot"]
users_collection = db["users"]
conversions_collection = db["conversions"]

DOWNLOAD_PATH = "downloads"
CONVERTED_PATH = "converted"

# Ensure directories exist
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(CONVERTED_PATH, exist_ok=True)

# Debug function
def log(msg):
    print(f"🔹 {msg}")

def update_user_stats(user_id):
    users_collection.update_one({"user_id": user_id}, {"$setOnInsert": {"quota": 10}}, upsert=True)

def update_conversion_stats(user_id):
    conversions_collection.insert_one({"user_id": user_id, "timestamp": os.times()})

def get_stats():
    total_users = users_collection.count_documents({})
    total_conversions = conversions_collection.count_documents({})
    return total_users, total_conversions

@bot.on_message(filters.command("convertfiletomedia"))
async def convert_file_to_media(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("Please reply to a file to convert it to media.")
        return

    file = message.reply_to_message.document
    file_path = os.path.join(DOWNLOAD_PATH, file.file_name)

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
        cmd = ["ffmpeg", "-i", downloaded, "-c:v", "libx264", output_file]
        subprocess.run(cmd, check=True)
        if not os.path.exists(output_file):
            log("❌ Conversion failed!")
            await message.reply("❌ Conversion failed.")
            return
        log(f"✅ Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg error: {e}")
        await message.reply("❌ FFmpeg conversion error.")
        return

    update_user_stats(message.from_user.id)
    update_conversion_stats(message.from_user.id)
    
    await message.reply("📤 Uploading media...")
    await message.reply_video(output_file, caption="Here is your converted media!")

@bot.on_message(filters.command("convertmediatofile"))
async def convert_media_to_file(client: Client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.audio):
        await message.reply("Please reply to a media file to convert it.")
        return

    media = message.reply_to_message.video or message.reply_to_message.audio
    media_path = os.path.join(DOWNLOAD_PATH, media.file_name)

    log(f"Downloading media: {media.file_name}")
    await message.reply("📥 Downloading media...")

    try:
        downloaded = await client.download_media(media, media_path)
        if not os.path.exists(downloaded):
            log("❌ Media download failed!")
            await message.reply("❌ Media download failed.")
            return
        log(f"✅ Media downloaded: {downloaded}")
    except Exception as e:
        log(f"❌ Download error: {e}")
        await message.reply("❌ Error downloading the media.")
        return

    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(media.file_name)[0] + ".mkv")

    log(f"🔄 Converting {media.file_name} to MKV...")
    await message.reply("⏳ Converting media to file...")

    try:
        cmd = ["ffmpeg", "-i", downloaded, "-c:v", "copy", "-c:a", "copy", output_file]
        subprocess.run(cmd, check=True)
        if not os.path.exists(output_file):
            log("❌ Conversion failed!")
            await message.reply("❌ Conversion failed.")
            return
        log(f"✅ Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg error: {e}")
        await message.reply("❌ FFmpeg conversion error.")
        return

    update_user_stats(message.from_user.id)
    update_conversion_stats(message.from_user.id)
    
    await message.reply("📤 Uploading converted file...")
    await message.reply_document(output_file, caption="Here is your converted file!")

@bot.on_message(filters.command("stats"))
async def stats_handler(client: Client, message: Message):
    total_users, total_conversions = get_stats()
    await message.reply(f"📊 **Bot Stats**:\n👥 Total Users: {total_users}\n🔄 Total Conversions: {total_conversions}")

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
