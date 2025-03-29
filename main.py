import os
from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
from flask import Flask
import threading
from commands import *  # Importing all the command functions from commands.py

# Logging function (FIX)
def log(msg):
    print(f"🔹 {msg}")

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

# Flask Webserver
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()

log("🚀 Bot is starting...")  # ✅ Ab ye error nahi dega
bot.run()
