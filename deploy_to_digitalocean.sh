#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check required environment variables
required_vars=(
    "DJANGO_SECRET_KEY"
    "DJANGO_ALLOWED_HOSTS"
    "POSTGRES_PASSWORD"
    "DO_SPACES_ACCESS_KEY"
    "DO_SPACES_SECRET_KEY"
    "DO_SPACES_BUCKET_NAME"
    "DOCKER_IMAGE_NAME"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set"
        exit 1
    fi
done

# Build and tag Docker image
echo "Building Docker image..."
docker-compose -f docker-compose.digitalocean.yml build

# Tag image for DigitalOcean registry
docker tag $DOCKER_IMAGE_NAME:latest registry.digitalocean.com/$DOCKER_IMAGE_NAME:latest

# Push to DigitalOcean registry
echo "Pushing to DigitalOcean registry..."
docker push registry.digitalocean.com/$DOCKER_IMAGE_NAME:latest

# Apply database migrations
echo "Applying database migrations..."
docker-compose -f docker-compose.digitalocean.yml run --rm web python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker-compose -f docker-compose.digitalocean.yml run --rm web python manage.py collectstatic --noinput

# Deploy stack to DigitalOcean
echo "Deploying to DigitalOcean..."
docker stack deploy -c docker-compose.digitalocean.yml quiz-app

echo "Deployment complete! Checking health..."
sleep 30

# Check application health
health_check() {
    status=$(curl -s -o /dev/null -w "%{http_code}" http://${DJANGO_ALLOWED_HOSTS}/health/)
    if [ $status -eq 200 ]; then
        echo "Application is healthy!"
        return 0
    else
        echo "Application health check failed with status: $status"
        return 1
    fi
}

# Retry health check a few times
max_retries=5
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if health_check; then
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Retrying health check in 10 seconds... ($retry_count/$max_retries)"
    sleep 10
done

if [ $retry_count -eq $max_retries ]; then
    echo "Warning: Application health check failed after $max_retries attempts"
    exit 1
fi

echo "Deployment successful!"
