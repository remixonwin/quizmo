FROM python:3.10-slim

# Copy version file first to bust cache
COPY version.txt /app/version.txt

# Install build essentials
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

# Create static directory and collect static files
RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "--timeout", "30", "--log-level", "info", "windsurf_app.wsgi:application"]
