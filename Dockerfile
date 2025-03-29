FROM python:3.12

# FFmpeg install करो
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# Dependencies install करो
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
