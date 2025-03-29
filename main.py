import os
import subprocess
import logging
from pyrogram import Client, filters
from pymongo import MongoClient
from flask import Flask
import threading

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Database Setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["FileToMediaBot"]
user_history = db["user_history"]

# Pyrogram Bot Setup
app = Client("file_media_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dummy Flask Server for Koyeb Health Check
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot is running!"
def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)
threading.Thread(target=run_flask, daemon=True).start()

# Start Command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        "\U0001F44B Welcome! Send a file or media and use the commands:\n\n"
        "\U0001F539 /convertfiletomedia - Convert file to media\n"
        "\U0001F539 /convertmediatofile - Convert media to file"
    )

# Convert File to Media
@app.on_message(filters.command("convertfiletomedia") & filters.private)
async def convert_file_to_media(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("Please reply to a file to convert it into media.")
    
    file_path = await message.reply_to_message.download()
    output_path = file_path.rsplit(".", 1)[0] + ".mp4"
    
    command = ["ffmpeg", "-i", file_path, "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", output_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    await message.reply_video(output_path)
    os.remove(file_path)
    os.remove(output_path)

# Convert Media to File
@app.on_message(filters.command("convertmediatofile") & filters.private)
async def convert_media_to_file(client, message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply_text("Please reply to a media file to convert it.")
    
    file_path = await message.reply_to_message.download()
    output_path = file_path.rsplit(".", 1)[0] + ".mkv"
    
    command = ["ffmpeg", "-i", file_path, "-c", "copy", output_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    await message.reply_document(output_path)
    os.remove(file_path)
    os.remove(output_path)

# Run the Bot
app.run()
