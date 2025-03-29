FROM python:3.9-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt first to cache dependencies
COPY requirements.txt .

# Install all dependencies properly
RUN pip install --no-cache-dir -r requirements.txt

# Copy all bot code
COPY . .

# Run the bot
CMD ["python", "main.py"]
