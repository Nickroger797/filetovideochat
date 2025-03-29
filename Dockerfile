FROM python:3.12

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set Work Directory
WORKDIR /app

# Copy All Files
COPY . .

# Install Dependencies
RUN pip install -r requirements.txt

# Give execution permission to main script (Optional, if needed)
RUN chmod +x /app/main.py

# Start the Bot
CMD ["python", "main.py"]
