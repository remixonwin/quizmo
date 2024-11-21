# Deploying to DigitalOcean

This guide will help you deploy the Quiz application to DigitalOcean using Docker and Docker Compose.

## Prerequisites

1. Docker and Docker Compose installed
2. DigitalOcean account
3. DigitalOcean CLI (doctl) installed and authenticated
4. Git repository with your code

## Setup Steps

1. Install doctl and authenticate:
   ```bash
   # Install doctl (Windows)
   scoop install doctl

   # Authenticate with your API token
   doctl auth init
   ```

2. Create a copy of the environment template:
   ```bash
   cp .env.example .env
   ```

3. Configure your environment variables in `.env`:
   - Generate a new Django secret key
   - Set your allowed hosts
   - Configure PostgreSQL credentials
   - Set up DigitalOcean Spaces credentials
   - Configure email settings
   - Set up monitoring settings

4. Create a DigitalOcean Container Registry:
   ```bash
   doctl registry create quiz-app-registry
   doctl registry login
   ```

5. Make the deployment script executable:
   ```bash
   chmod +x deploy_to_digitalocean.sh
   ```

6. Run the deployment script:
   ```bash
   ./deploy_to_digitalocean.sh
   ```

## Environment Variables

The following environment variables must be set before deployment:

### Required Variables
- `DJANGO_SECRET_KEY`: Your Django secret key
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `POSTGRES_PASSWORD`: Database password
- `DO_SPACES_ACCESS_KEY`: DigitalOcean Spaces access key
- `DO_SPACES_SECRET_KEY`: DigitalOcean Spaces secret key
- `DO_SPACES_BUCKET_NAME`: DigitalOcean Spaces bucket name
- `DOCKER_IMAGE_NAME`: Name for your Docker image

### Optional Variables
- `WEB_REPLICAS`: Number of web service replicas (default: 2)
- `SENTRY_DSN`: Sentry DSN for error tracking
- `DJANGO_LOG_LEVEL`: Django logging level (default: INFO)
- `APP_LOG_LEVEL`: Application logging level (default: INFO)

## Health Monitoring

The application includes a health check endpoint at `/health/` that monitors:
- Database connectivity
- Redis connection
- System resources (CPU and memory usage)
- Application status

Health check responses:
- 200: Application is healthy
- 503: One or more components are unhealthy

## Monitoring and Logs

1. View application health:
   ```bash
   curl https://your-app-domain/health/
   ```

2. View container logs:
   ```bash
   # View logs for web service
   docker service logs quiz-app_web

   # View logs for specific container
   docker logs <container_id>
   ```

3. Monitor resources:
   ```bash
   # View service status
   docker service ls

   # View container stats
   docker stats
   ```

## Scaling

To scale the web service:
```bash
docker service scale quiz-app_web=3
```

## Troubleshooting

1. If deployment fails:
   - Check the deployment script output
   - Verify environment variables are set correctly
   - Check Docker registry authentication
   - Verify DigitalOcean credentials

2. If health check fails:
   - Check database connectivity
   - Verify Redis connection
   - Monitor system resources
   - Review application logs

3. Common issues:
   - Database migration failures: Check migration logs
   - Static files missing: Verify DO Spaces configuration
   - Connection errors: Check network and firewall settings

## Rollback

To rollback to a previous version:
```bash
# List available images
docker image ls

# Deploy previous version
docker service update --image registry.digitalocean.com/$DOCKER_IMAGE_NAME:previous quiz-app_web
```

## Support

If you encounter issues:
1. Check application logs
2. Review health check endpoint
3. Monitor system resources
4. Contact support if needed
