from pyrogram import filters
from pyrogram.types import Message
import os
import subprocess
import shutil

# Directories
DOWNLOAD_LOCATION = "./DOWNLOADS"
CONVERTED_PATH = "./CONVERTED"
FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"

def log(msg):
    print(f"🔹 {msg}")

async def start_command(client, message: Message):
    await message.reply("Hello! I am your File Converter Bot. Send me a file to convert.")

async def convert_file_to_media(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("Please reply to a file to convert it to media.")
        return

    file = message.reply_to_message.document
    safe_filename = "".join(c for c in file.file_name if c.isalnum() or c in ('.', '_', '-'))
    
    file_path = os.path.join(DOWNLOAD_LOCATION, safe_filename)

    log(f"Downloading file: {file.file_name}")
    await message.reply("📥 Downloading file...")

    downloaded = await client.download_media(file, file_path)
    if not os.path.exists(downloaded):
        await message.reply("❌ File download failed.")
        return
    log(f"✅ File downloaded: {downloaded}")

    os.makedirs(CONVERTED_PATH, exist_ok=True)  # Ensure output directory exists
    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(safe_filename)[0] + ".mp4")

    log(f"🔄 Converting {file.file_name} to MP4...")
    await message.reply("⏳ Converting file to media...")

    cmd = [FFMPEG_PATH, "-i", downloaded, "-c:v", "libx264", output_file]
    subprocess.run(cmd, check=True)

    if not os.path.exists(output_file):
        await message.reply("❌ Conversion failed.")
        return
    log(f"✅ Conversion successful: {output_file}")

    await message.reply_video(output_file, caption="Here is your converted media!")

async def convert_media_to_file(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        await message.reply("Please reply to a video to convert it to a file.")
        return

    video = message.reply_to_message.video
    file_path = os.path.join(DOWNLOAD_LOCATION, video.file_name)

    log(f"Downloading video: {video.file_name}")
    await message.reply("📥 Downloading video...")

    downloaded = await client.download_media(video, file_path)
    if not os.path.exists(downloaded):
        await message.reply("❌ Video download failed.")
        return
    log(f"✅ Video downloaded: {downloaded}")

    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(video.file_name)[0] + ".zip")
    log(f"🔄 Converting {video.file_name} to a zip file...")
    await message.reply("⏳ Converting media to file...")

    shutil.make_archive(output_file.replace(".zip", ""), "zip", DOWNLOAD_LOCATION)

    if not os.path.exists(output_file):
        await message.reply("❌ Conversion failed.")
        return
    log(f"✅ Conversion successful: {output_file}")

    await message.reply_document(output_file, caption="Here is your converted file!")

async def stats_command(client, message: Message, stats_collection):
    stats = await stats_collection.find_one({"_id": "conversion_stats"})
    total_conversions = stats.get("total_conversions", 0) if stats else 0
    await message.reply(f"📊 Total Conversions: {total_conversions}")
