# Use official Python image
FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set Work Directory
WORKDIR /app

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose any necessary ports (if using a web framework)
EXPOSE 8080

# Start the Bot
CMD ["python", "main.py"]
