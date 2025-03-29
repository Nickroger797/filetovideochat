import os
import subprocess
import shutil
from pyrogram import Client

# Directories
DOWNLOAD_LOCATION = "./DOWNLOADS"
CONVERTED_PATH = "./CONVERTED"

# FFmpeg path check
FFMPEG_PATH = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError("FFmpeg not found! Install it in your system.")

async def convert_file(file_id, client: Client):
    # Fetch the file information using file_id
    file = await client.get_messages(file_id)
    file_path = os.path.join(DOWNLOAD_LOCATION, file.file_name)

    # Download file
    print(f"Downloading file: {file.file_name}")
    try:
        downloaded = await client.download_media(file, file_path)
        if not os.path.exists(downloaded):
            print("❌ File download failed.")
            return None
        print(f"✅ File downloaded: {downloaded}")
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

    # Define the output file name and path (e.g., convert to MP4)
    output_file = os.path.join(CONVERTED_PATH, os.path.splitext(file.file_name)[0] + ".mp4")

    # Converting the file using FFmpeg
    print(f"🔄 Converting {file.file_name} to MP4...")
    cmd = [FFMPEG_PATH, "-i", downloaded, "-c:v", "libx264", output_file]
    try:
        subprocess.run(cmd, check=True)
        if not os.path.exists(output_file):
            print("❌ Conversion failed.")
            return None
        print(f"✅ Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")
        return None

    return output_file
