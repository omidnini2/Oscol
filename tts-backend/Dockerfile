FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y git ffmpeg && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir TTS==0.22.0 Flask==2.3.3 Flask-Cors==4.0.0 langdetect==1.0.9

# Copy backend code
COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]