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

# Wrapper function for stats command
async def stats_command_wrapper(client, message):
    await commands.stats_command(client, message, stats_collection)

# 🔹 Register Handlers
bot.add_handler(filters.command("start")(commands.start_command))
bot.add_handler(filters.command("convertfiletomedia")(commands.convert_file_to_media))
bot.add_handler(filters.command("convertmediatofile")(commands.convert_media_to_file))
bot.add_handler(filters.command("stats")(stats_command_wrapper))  # ✅ Fix applied

print("🚀 Bot is starting...")
bot.run()
