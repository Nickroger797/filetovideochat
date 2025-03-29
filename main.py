import os
import asyncio
import ffmpeg
import pymongo
from pyrogram import Client, filters
from pyrogram.types import Message

# Bot credentials
API_ID = int(os.getenv("API_ID"))  # API_ID ko integer me convert kar rahe hain
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")


# MongoDB setup
client_db = pymongo.MongoClient(MONGO_URI)
db = client_db["FileMediaBot"]
users_collection = db["users"]
logs_collection = db["logs"]

app = Client("FileMediaConverter", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def update_user_data(user_id):
    users_collection.update_one({"user_id": user_id}, {"$inc": {"conversions": 1}}, upsert=True)

def log_conversion(user_id, file_type, file_size, duration):
    logs_collection.insert_one({
        "user_id": user_id,
        "file_type": file_type,
        "file_size": file_size,
        "duration": duration
    })

# Start Command
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("👋 Welcome! Send a file or media and use the commands:\n\n🔹 /convertfiletomedia - Convert file to media\n🔹 /convertmediatofile - Convert media to file")

# Convert File to Media
@app.on_message(filters.command("convertfiletomedia") & filters.document)
async def convert_file_to_media(client: Client, message: Message):
    user_id = message.from_user.id
    file_path = await message.download()
    output_path = file_path + ".mp4"  # Assuming video conversion
    
    try:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", file_path, "-c:v", "libx264", "-preset", "fast", "-crf", "23", output_path
        )
        await process.communicate()
        
        file_size = os.path.getsize(output_path)
        update_user_data(user_id)
        log_conversion(user_id, "file_to_media", file_size, None)
        
        await message.reply_video(output_path)
        os.remove(output_path)
    except Exception as e:
        await message.reply_text(f"Conversion failed: {str(e)}")
    finally:
        os.remove(file_path)

# Convert Media to File
@app.on_message(filters.command("convertmediatofile") & (filters.video | filters.audio | filters.photo))
async def convert_media_to_file(client: Client, message: Message):
    user_id = message.from_user.id
    media_path = await message.download()
    output_path = media_path + ".file"
    
    try:
        os.rename(media_path, output_path)
        file_size = os.path.getsize(output_path)
        update_user_data(user_id)
        log_conversion(user_id, "media_to_file", file_size, None)
        
        await message.reply_document(output_path)
        os.remove(output_path)
    except Exception as e:
        await message.reply_text(f"Conversion failed: {str(e)}")

from flask import Flask  
import threading  

flask_app = Flask(__name__)  

@flask_app.route('/')  
def home():  
    return "Bot is running!"  

def run_flask():  
    flask_app.run(host="0.0.0.0", port=8080)  

# Flask ko ek alag thread pe run karna  
threading.Thread(target=run_flask, daemon=True).start()  

app.run()
