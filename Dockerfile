FROM python:3.12

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set Work Directory
WORKDIR /app

# Copy All Files
COPY . .

# Give Executable Permission to startup.sh
RUN chmod +x startup.sh

# Install Dependencies
RUN pip install -r requirements.txt

# Start the Bot
CMD ["./startup.sh"]
