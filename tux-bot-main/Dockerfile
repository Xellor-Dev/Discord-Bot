FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libsqlite3-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python main.py & tail -f /dev/null"]
