FROM python:3.12

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set Work Directory
WORKDIR /app

# Copy All Files
COPY . .

# Give Execute Permission to startup.sh
RUN chmod +x /app/startup.sh

# Install Dependencies
RUN pip install -r requirements.txt

# Start the Bot using Shell
CMD ["/bin/bash", "-c", "/app/startup.sh"]
