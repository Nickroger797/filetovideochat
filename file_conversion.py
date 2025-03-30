import os
import subprocess
import shutil
from pyrogram import Client
from pyrogram.types import Message

# Directories
DOWNLOAD_LOCATION = "./DOWNLOADS"
CONVERTED_PATH = "./CONVERTED"

# FFmpeg path check
FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError("FFmpeg not found! Install it in your system.")

def log(msg):
    print(f"🔹 {msg}")

# Function to send logs to Telegram
async def send_logs_to_telegram(client: Client, chat_id, log_file):
    with open(log_file, "r") as file:
        log_text = file.read()[-4000:]  # सिर्फ़ आख़िरी 4000 characters भेजेंगे ताकि message limit exceed न हो
    await client.send_message(chat_id, f"🔹 **FFmpeg Logs:**\n\n<pre>{log_text}</pre>", parse_mode="html")
    
# Function to convert file
async def convert_file(file, client: Client, message: Message):
    file_path = os.path.join(DOWNLOAD_LOCATION, file.file_name)
    
    log(f"Downloading file: {file.file_name}")
    await message.reply("📥 Downloading file...")

    try:
        downloaded = await client.download_media(file, file_path)
        if not os.path.exists(downloaded):
            await message.reply("❌ File download failed.")
            return
        log(f"✅ File downloaded: {downloaded}")
    except Exception as e:
        log(f"❌ Download error: {e}")
        await message.reply("❌ Error downloading the file.")
        return

    # Conversion logic
    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(file.file_name)[0] + ".mp4")
    log(f"🔄 Converting {file.file_name} to MP4...")
    await message.reply("⏳ Converting file to media...")

    log_file = "ffmpeg_log.txt"  # Log file path

    try:
        cmd = [FFMPEG_PATH, "-y", "-i", downloaded, "-c:v", "libx264", output_file]
        
        with open(log_file, "w") as log_file_obj:
            process = subprocess.run(cmd, stdout=log_file_obj, stderr=log_file_obj, check=False)
        
        if process.returncode != 0 or not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            await message.reply("❌ FFmpeg conversion failed. Sending logs...")
            await send_logs_to_telegram(client, message.chat.id, log_file)
            return

        log(f"✅ Conversion successful: {output_file}")
        await message.reply_video(output_file, caption="Here is your converted media!")

    except Exception as e:
        log(f"❌ FFmpeg error: {e}")
        await message.reply("❌ FFmpeg conversion error.")

# Handle conversion from any document received
async def handle_conversion(client, message):
    if not message.document:
        await message.reply("Please send a document to convert.")
        return

    # Directly use message.document for file
    file = message.document
    await convert_file(file, client, message)  # Call the conversion function
