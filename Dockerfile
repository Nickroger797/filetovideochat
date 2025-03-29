FROM python:3.12-slim

# आवश्यक पैकेज इंस्टॉल करें
RUN apt-get update && apt-get install -y ffmpeg

# वर्किंग डायरेक्टरी सेट करें
WORKDIR /app

# आवश्यक फाइलें कॉपी करें
COPY requirements.txt .
COPY main.py .
COPY startup.sh .  # ✅ startup.sh को कॉपी किया

# आवश्यक पायथन पैकेज इंस्टॉल करें
RUN pip install --no-cache-dir -r requirements.txt

# startup.sh को executable बनाएं
RUN chmod +x startup.sh

# बॉट शुरू करें
CMD ["./startup.sh"]
