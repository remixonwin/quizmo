FROM python:3.11.7-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psycopg2-binary==2.9.9 gunicorn==21.2.0 psycopg==3.1.18

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=windsurf_app.settings_digitalocean \
    DEBUG=0 \
    PYTHONPATH=/app

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Run as non-root user
RUN groupadd -r django && useradd -r -g django django && \
    chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "sync", "--timeout", "30", "--log-level", "info", "windsurf_app.wsgi:application"]
