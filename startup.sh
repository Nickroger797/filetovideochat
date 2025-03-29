#!/bin/bash

# Update & Install FFmpeg
apt-get update && apt-get install -y ffmpeg

# Start the Bot
python main.py
