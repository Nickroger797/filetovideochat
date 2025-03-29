FROM python:3.9-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install pyrogram motor Flask

# Copy your bot code
COPY . /app

WORKDIR /app

CMD ["python", "main.py"]
