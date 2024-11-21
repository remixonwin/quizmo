#!/bin/bash

# Exit on error
set -e

# Check if DIGITAL_OCEAN_TOKEN is set
if [ -z "$DIGITAL_OCEAN_TOKEN" ]; then
    echo "Error: DIGITAL_OCEAN_TOKEN environment variable is not set"
    echo "Please run: export DIGITAL_OCEAN_TOKEN=your_token"
    exit 1
fi

# Check if APP_NAME is set
if [ -z "$APP_NAME" ]; then
    echo "Error: APP_NAME environment variable is not set"
    echo "Please run: export APP_NAME=your_app_name"
    exit 1
fi

# Login to DigitalOcean Container Registry
echo "Logging in to DigitalOcean Container Registry..."
doctl auth init --access-token $DIGITAL_OCEAN_TOKEN

# Create app spec file
cat > app.yaml << EOL
name: $APP_NAME
region: nyc
services:
  - name: web
    github:
      repo: your-github-username/quiz-app
      branch: main
    dockerfile_path: Dockerfile
    source_dir: /
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs
    routes:
      - path: /
    envs:
      - key: DJANGO_SETTINGS_MODULE
        value: windsurf_app.settings_docker
      - key: DJANGO_SECRET_KEY
        value: \${DJANGO_SECRET_KEY}
      - key: DJANGO_ALLOWED_HOSTS
        value: \${APP_URL}
      - key: POSTGRES_DB
        value: \${POSTGRES_DB}
      - key: POSTGRES_USER
        value: \${POSTGRES_USER}
      - key: POSTGRES_PASSWORD
        value: \${POSTGRES_PASSWORD}
      - key: POSTGRES_HOST
        value: \${POSTGRES_HOST}
      - key: POSTGRES_PORT
        value: "5432"
  
  databases:
    - engine: PG
      name: quiz-db
      num_nodes: 1
      size: db-s-dev-database
      version: "15"
EOL

# Deploy the app
echo "Deploying app to DigitalOcean..."
doctl apps create --spec app.yaml

echo "Deployment complete! Your app will be available at: https://$APP_NAME.ondigitalocean.app"
