import os
from motor.motor_asyncio import AsyncIOMotorClient
from flask import Flask
import threading
import commands
from pyrogram import Client, filters

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

# 🔹 Commands Register Here
bot.add_handler(commands.start_command, filters.command("start"))
bot.add_handler(commands.convert_file_to_media, filters.command("convertfiletomedia"))
bot.add_handler(commands.convert_media_to_file, filters.command("convertmediatofile"))
bot.add_handler(commands.stats_command, filters.command("stats"), stats_collection)

print("🚀 Bot is starting...")
bot.run()
