# Dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libxml2-dev \
    libxslt1-dev \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/shopsite
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "shopsite.wsgi:application", "--bind", "0.0.0.0:8000"]
