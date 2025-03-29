import os
import subprocess
import shutil
from pyrogram import Client
from pyrogram.types import Message
import asyncio

# Directories
DOWNLOAD_LOCATION = "./DOWNLOADS"
CONVERTED_PATH = "./CONVERTED"

# FFmpeg path check
FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError("FFmpeg not found! Install it in your system.")

def log(msg):
    print(f"🔹 {msg}")

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

    # Conversion logic here
    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(file.file_name)[0] + ".mp4")

    log(f"🔄 Converting {file.file_name} to MP4...")
    await message.reply("⏳ Converting file to media...")

    try:
        cmd = [FFMPEG_PATH, "-i", downloaded, "-c:v", "libx264", output_file]
        subprocess.run(cmd, check=True)
        if not os.path.exists(output_file):
            await message.reply("❌ Conversion failed.")
            return
        log(f"✅ Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg error: {e}")
        await message.reply("❌ FFmpeg conversion error.")
        return

    await message.reply_video(output_file, caption="Here is your converted media!")

# Handle conversion from any document received
async def handle_conversion(client, message):
    if not message.document:
        await message.reply("Please send a document to convert.")
        return

    # Directly use message.document for file
    file = message.document
    await convert_file(file, client, message)  # Call the conversion function
