import os
import subprocess
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from file_conversion import convert_file  # Import the function
from file_conversion import handle_conversion

# Directories
DOWNLOAD_LOCATION = "./DOWNLOADS"
CONVERTED_PATH = "./CONVERTED"

# FFmpeg path check
FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError("FFmpeg not found! Install it in your system.")

def log(msg):
    print(f"🔹 {msg}")

async def update_stats(stats_collection):
    await stats_collection.update_one({"_id": "conversion_stats"}, {"$inc": {"total_conversions": 1}}, upsert=True)

# Command to convert file to media
@Client.on_message(filters.command("convertfiletomedia"))
async def convert_file_to_media(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("Please reply to a file to convert it to media.")
        return

    file = message.reply_to_message.document
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
        await update_stats()
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg error: {e}")
        await message.reply("❌ FFmpeg conversion error.")
        return

    await message.reply_video(output_file, caption="Here is your converted media!")

# Command to convert media to file
@Client.on_message(filters.command("convertmediatofile"))
async def convert_media_to_file(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        await message.reply("Please reply to a video to convert it to a file.")
        return

    video = message.reply_to_message.video
    file_path = os.path.join(DOWNLOAD_LOCATION, video.file_name)

    log(f"Downloading video: {video.file_name}")
    await message.reply("📥 Downloading video...")

    try:
        downloaded = await client.download_media(video, file_path)
        if not os.path.exists(downloaded):
            await message.reply("❌ Video download failed.")
            return
        log(f"✅ Video downloaded: {downloaded}")
    except Exception as e:
        log(f"❌ Download error: {e}")
        await message.reply("❌ Error downloading the video.")
        return

    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(video.file_name)[0] + ".zip")

    log(f"🔄 Converting {video.file_name} to a zip file...")
    await message.reply("⏳ Converting media to file...")

    try:
        shutil.make_archive(output_file.replace(".zip", ""), "zip", DOWNLOAD_LOCATION)
        if not os.path.exists(output_file):
            await message.reply("❌ Conversion failed.")
            return
        log(f"✅ Conversion successful: {output_file}")
        await update_stats()
    except Exception as e:
        log(f"❌ Compression error: {e}")
        await message.reply("❌ Compression error.")
        return

    await message.reply_document(output_file, caption="Here is your converted file!")

# Command to get stats
@Client.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message, stats_collection):
    stats = await stats_collection.find_one({"_id": "conversion_stats"})
    total_conversions = stats.get("total_conversions", 0) if stats else 0
    await message.reply(f"📊 Total Conversions: {total_conversions}")

@Client.on_message(filters.document)
async def on_document_received(client: Client, message: Message):
    await handle_conversion(client, message)
