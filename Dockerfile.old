FROM python:3.13.0-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=windsurf_app.settings_digitalocean \
    DEBUG=0

# Create directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start gunicorn with optimized settings
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "--max-requests", "1000", "--max-requests-jitter", "50", "--timeout", "30", "--keep-alive", "5", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "windsurf_app.wsgi:application"]
