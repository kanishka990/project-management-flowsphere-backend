FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# requirements.txt is UTF-16
RUN iconv -f UTF-16 -t UTF-8 requirements.txt > requirements-utf8.txt \
    && pip install --no-cache-dir -r requirements-utf8.txt

COPY backend .

EXPOSE 6000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","6000"]
