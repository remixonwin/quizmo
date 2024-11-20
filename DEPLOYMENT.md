# Minnesota DMV Practice Quiz App - DigitalOcean Deployment Guide

## Prerequisites

1. Accounts Required:
   - DigitalOcean account
   - Namecheap account
   - Docker Hub account (optional, for private images)

2. Local Setup:
   - Docker and Docker Compose installed
   - doctl (DigitalOcean CLI) installed
   - Git installed

## Step 1: DigitalOcean Setup

1. Create a new Droplet:
   ```bash
   # Log in to DigitalOcean
   doctl auth init

   # Create Droplet (4GB RAM minimum recommended)
   doctl compute droplet create mnpracticetest \
     --size s-2vcpu-4gb \
     --image docker-20.10.21 \
     --region nyc1 \
     --ssh-keys <your-ssh-key-id>
   ```

2. Configure Firewall:
   - Go to DigitalOcean Dashboard → Networking → Firewalls
   - Create new firewall with rules:
     - Inbound: Allow HTTP (80), HTTPS (443), SSH (22)
     - Outbound: Allow all
   - Apply to your droplet

## Step 2: Domain Configuration

1. Namecheap DNS Setup:
   - Log in to Namecheap
   - Go to Domain List → Manage
   - Navigate to Advanced DNS
   - Add/Update these records:
     ```
     A Record:
     Host: @
     Value: <Your-Droplet-IP>
     TTL: Automatic

     A Record:
     Host: www
     Value: <Your-Droplet-IP>
     TTL: Automatic
     ```

2. Configure SSL with Let's Encrypt:
   ```bash
   # SSH into your droplet
   ssh root@<Your-Droplet-IP>

   # Install Certbot
   apt-get update
   apt-get install certbot python3-certbot-nginx

   # Get SSL certificate
   certbot --nginx -d mnpracticetest.com -d www.mnpracticetest.com
   ```

## Step 3: Server Setup

1. SSH into your droplet:
   ```bash
   ssh root@<Your-Droplet-IP>
   ```

2. Install required packages:
   ```bash
   apt-get update
   apt-get install -y \
     python3-pip \
     python3-dev \
     postgresql \
     postgresql-contrib \
     nginx \
     redis-server
   ```

3. Create PostgreSQL database:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE mnquiz_db;
   CREATE USER mnquiz_user WITH PASSWORD 'your-secure-password';
   GRANT ALL PRIVILEGES ON DATABASE mnquiz_db TO mnquiz_user;
   \q
   ```

## Step 4: Application Deployment

1. Clone repository:
   ```bash
   git clone https://github.com/your-org/mnpracticetest.git
   cd mnpracticetest
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with production values:
   nano .env
   ```

3. Deploy with Docker Compose:
   ```bash
   # Build and start containers
   docker-compose -f docker-compose.yml up -d

   # Run migrations
   docker-compose exec web python manage.py migrate

   # Collect static files
   docker-compose exec web python manage.py collectstatic --no-input

   # Create superuser
   docker-compose exec web python manage.py createsuperuser
   ```

## Step 5: DigitalOcean Monitoring Setup

1. Install DigitalOcean Monitoring Agent:
   ```bash
   curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash
   ```

2. Enable monitoring in DigitalOcean dashboard:
   - Go to Droplet → Graphs
   - Click "Enable Monitoring"

## Step 6: Backup Configuration

1. Enable DigitalOcean Backups:
   - Go to Droplet settings
   - Enable backups

2. Set up database backups:
   ```bash
   # Create backup directory
   mkdir -p /root/backups

   # Create backup script
   cat > /root/backup.sh << 'EOF'
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/root/backups"
   
   # Database backup
   docker-compose exec -T db pg_dump -U mnquiz_user mnquiz_db > "$BACKUP_DIR/db_$DATE.sql"
   
   # Compress backup
   gzip "$BACKUP_DIR/db_$DATE.sql"
   
   # Keep only last 7 days of backups
   find "$BACKUP_DIR" -type f -mtime +7 -delete
   EOF

   # Make script executable
   chmod +x /root/backup.sh

   # Add to crontab (runs daily at 2 AM)
   (crontab -l 2>/dev/null; echo "0 2 * * * /root/backup.sh") | crontab -
   ```

## Step 7: Monitoring and Maintenance

1. Set up log rotation:
   ```bash
   cat > /etc/logrotate.d/mnquiz << 'EOF'
   /var/log/mnquiz/*.log {
       daily
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
       sharedscripts
       postrotate
           systemctl reload nginx
       endscript
   }
   EOF
   ```

2. Configure monitoring alerts:
   - Go to DigitalOcean → Monitoring → Alerts
   - Set up alerts for:
     - CPU usage > 80%
     - Memory usage > 80%
     - Disk usage > 80%
     - HTTP errors > 1%

## Step 8: SSL/TLS Configuration

1. Update Nginx SSL configuration:
   ```bash
   # Verify SSL configuration
   nginx -t

   # Reload Nginx
   systemctl reload nginx
   ```

2. Test SSL setup:
   - Visit https://www.ssllabs.com/ssltest/
   - Enter your domain
   - Ensure A+ rating

## Step 9: Performance Optimization

1. Enable Nginx caching:
   ```bash
   # Create cache directory
   mkdir -p /var/cache/nginx/proxy_cache
   chown -R www-data:www-data /var/cache/nginx
   ```

2. Configure Redis:
   ```bash
   # Optimize Redis configuration
   sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
   sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
   systemctl restart redis
   ```

## Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Update application
git pull
docker-compose down
docker-compose up -d
docker-compose exec web python manage.py migrate

# Backup database manually
./backup.sh

# Monitor resource usage
htop

# Check SSL certificate
certbot certificates
```

## Troubleshooting

1. Check application status:
   ```bash
   docker-compose ps
   docker-compose logs web
   ```

2. Test database connection:
   ```bash
   docker-compose exec web python manage.py dbshell
   ```

3. Check Nginx configuration:
   ```bash
   nginx -t
   ```

## Security Notes

1. Keep system updated:
   ```bash
   apt-get update
   apt-get upgrade
   ```

2. Monitor security logs:
   ```bash
   tail -f /var/log/auth.log
   ```

3. Check SSL certificate expiry:
   ```bash
   certbot certificates
   ```

## Contact Information

- Technical Support: support@mnpracticetest.com
- Security Issues: security@mnpracticetest.com

## Useful Links

- [DigitalOcean Documentation](https://docs.digitalocean.com)
- [Namecheap DNS Documentation](https://www.namecheap.com/support/knowledgebase/article.aspx/434/2237/how-do-i-set-up-host-records-for-a-domain/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
