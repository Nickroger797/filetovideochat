# file_conversion.py
import asyncio
from pyrogram.errors import TimeoutError, FloodWait
import ffmpeg
import os

# Retry logic for file download
async def download_file(file_id, client, retries=3, timeout=60):
    for attempt in range(retries):
        try:
            # File download with increased timeout
            file = await client.get_file(file_id, timeout=timeout)
            return file  # Return file if download is successful
        except TimeoutError:
            print(f"Attempt {attempt + 1}: Request timed out, retrying...")
            await asyncio.sleep(5)  # Wait before retrying
        except FloodWait as e:
            print(f"Flood wait for {e.x} seconds.")
            await asyncio.sleep(e.x)  # Handle flood wait
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit if any other exception occurs
    raise Exception("Failed to download file after multiple retries")

# File conversion logic with ffmpeg
async def convert_file(file_id, client):
    try:
        # Download the file with retry logic
        file = await download_file(file_id, client)
        print(f"Downloaded file: {file.file_path}")
        
        # Specify the input file path and output path
        input_path = f"./DOWNLOADS/{file.file_path.split('/')[-1]}"
        output_path = f"./CONVERTED/{file.file_path.split('/')[-1].replace('.mkv', '.mp4')}"
        
        # Using ffmpeg to convert the file
        ffmpeg.input(input_path).output(output_path).run()
        print(f"Conversion successful, output saved to: {output_path}")
        
        # Add any further processing here (e.g., sending the file back to the user)
        
    except Exception as e:
        print(f"Error during conversion: {e}")
