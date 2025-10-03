# Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data/source data/raw data/normalized db logs

CMD ["python", "src/search_cli.py", "--help"]
