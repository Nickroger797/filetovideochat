FROM debian:bookworm-slim

# FFmpeg और dependencies इंस्टॉल करो
RUN apt-get update && apt-get install -y ffmpeg python3 python3-pip

WORKDIR /app

COPY requirements.txt .
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
