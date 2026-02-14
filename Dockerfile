FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir flask gunicorn
RUN pip install --no-cache-dir "yt-dlp @ https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz"


EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--timeout", "120", "app:app"]
