import os
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from flask import Flask
import threading
import commands

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
stats_collection = db["stats"]

# Flask Webserver
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()

# Register Handlers
@bot.on_message(filters.command("start"))
async def start(client, message):
    await commands.start_command(client, message)

@bot.on_message(filters.command("convertfiletomedia"))
async def convert_file(client, message):
    await commands.convert_file_to_media(client, message)

@bot.on_message(filters.command("convertmediatofile"))
async def convert_media(client, message):
    await commands.convert_media_to_file(client, message)

@bot.on_message(filters.command("stats"))
async def stats_command(client, message):
    await commands.stats_command(client, message, stats_collection)  # ✅ Fix applied

print("🚀 Bot is starting...")
bot.run()
