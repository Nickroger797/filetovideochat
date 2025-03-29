apt update && apt install -y ffmpeg
export PATH=$PATH:/usr/bin  # Ensure ffmpeg is accessible
which ffmpeg  # Debugging ke liye
python main.py
