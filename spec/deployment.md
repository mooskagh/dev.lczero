# LCZero Dev Portal Deployment Guide

## The state of the destination machine

* The username is `lc0`
* User has sudo privileges
* The `dev.lczero.org` domain is already set up to point to the server (through Cloudflare proxy)
* There is nginx installed.
* The server has a PostgreSQL server running.
* The installation should be in `~/lczero_dev_portal/` directory
* We'll need a subdirectory where we'll check out the code, and another subdirectory where we'll run the server (probably both independent git clones)
* We want to set up the server to start through systemd
* Use wsgi rather than asgi for now.
* The repository is at <https://github.com/mooskagh/lczero_dev_portal>
* Quite recent Python is installed, also there is pyenv.
* In general, the system there is Debian trixie (i.e. current testing)

## Detailed Deployment Instructions

## 1. Initial Setup and Dependencies

### 1.1 Connect to the production server

```bash
ssh lc0@dev.lczero.org
```

### 1.2 Install system dependencies

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git postgresql-client nginx-full
```

### 1.3 Verify PostgreSQL is running

```bash
sudo systemctl status postgresql
```

## 2. Directory Structure Setup

### 2.1 Create the main project directory

```bash
mkdir -p ~/lczero_dev_portal
cd ~/lczero_dev_portal
```

### 2.2 Create subdirectories for deployment

```bash
# Directory for the production code (stable releases)
mkdir -p production

# Directory for staging/testing deployments
mkdir -p staging

# Directory for shared resources
mkdir -p shared/logs
mkdir -p shared/static
mkdir -p shared/media
mkdir -p shared/artifacts
```

## 3. Code Deployment

### 3.1 Clone the repository for production

```bash
cd ~/lczero_dev_portal/production
git clone https://github.com/mooskagh/dev.lczero.git lczero_dev_portal
```

### 3.2 Create Python virtual environment

```bash
cd ~/lczero_dev_portal/production
python3 -m venv venv
source venv/bin/activate
```

### 3.3 Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # WSGI server for production
```

## 4. Database Setup

### 4.1 Create PostgreSQL database and user

```bash
sudo -u postgres psql
```

In PostgreSQL prompt:

```sql
CREATE DATABASE lczero_dev_portal;
CREATE USER lczero_prod WITH PASSWORD 'secure_production_password_here';
GRANT ALL PRIVILEGES ON DATABASE lczero_dev_portal TO lczero_prod;
ALTER USER lczero_prod CREATEDB;  -- For running tests if needed
\q
```

### 4.2 Test database connection

```bash
psql -h localhost -U lczero_prod -d lczero_dev_portal -c "SELECT version();"
```

## 5. Environment Configuration

### 5.1 Create production environment file

```bash
cd ~/lczero_dev_portal/production
cp .env.sample .env
```

### 5.2 Edit the production environment file

```bash
nano .env
```

Configure with production values:

```bash
# Database Configuration
DATABASE_URL=postgres://lczero_prod:secure_production_password_here@localhost:5432/lczero_dev_portal

# Security Settings
DEBUG=False
SECRET_KEY=generate_a_secure_secret_key_here
ALLOWED_HOSTS=dev.lczero.org,127.0.0.1,localhost

# Discord OAuth2 Configuration (get from Discord Developer Portal)
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret

# Artifacts Configuration
ARTIFACTS_STORAGE_PATH=/home/lc0/lczero_dev_portal/shared/artifacts
ARTIFACTS_UPLOAD_TOKEN=secure_upload_token_here
ARTIFACTS_DOWNLOAD_URL_PREFIX=/static/artifacts
ARTIFACTS_RETENTION_DAYS=30
ARTIFACTS_PR_RETENTION_DAYS=7
ARTIFACTS_MAX_FILE_SIZE=1073741824
```

### 5.3 Generate a secure Django secret key

```bash
cd ~/lczero_dev_portal/production
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and update SECRET_KEY in .env file.

## 6. Django Application Setup

### 6.1 Run Django system checks

```bash
cd ~/lczero_dev_portal/production/lczero_dev_portal
source ../venv/bin/activate
python manage.py check --verbosity=2
```

### 6.2 Run database migrations

```bash
python manage.py migrate
```

### 6.3 Create superuser account

```bash
python manage.py createsuperuser
```

### 6.4 Collect static files

```bash
python manage.py collectstatic --noinput
```

### 6.5 Test the application
```bash
python manage.py runserver 127.0.0.1:8000
```
Test in another terminal: `curl http://127.0.0.1:8000/`

## 7. Gunicorn Configuration

### 7.1 Create Gunicorn configuration file
```bash
cd ~/lczero_dev_portal/production
nano gunicorn.conf.py
```

Add the following configuration:
```python
# Gunicorn configuration file
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "lc0"
group = "lc0"
tmp_upload_dir = None
errorlog = "/home/lc0/lczero_dev_portal/shared/logs/gunicorn_error.log"
accesslog = "/home/lc0/lczero_dev_portal/shared/logs/gunicorn_access.log"
loglevel = "info"
```

### 7.2 Create Gunicorn startup script
```bash
cd ~/lczero_dev_portal/production
nano start_gunicorn.sh
```

Add the following:
```bash
#!/bin/bash
cd /home/lc0/lczero_dev_portal/production/lczero_dev_portal
source /home/lc0/lczero_dev_portal/production/venv/bin/activate
exec gunicorn -c /home/lc0/lczero_dev_portal/production/gunicorn.conf.py lczero_dev_portal.wsgi:application
```

Make it executable:
```bash
chmod +x start_gunicorn.sh
```

### 7.3 Test Gunicorn
```bash
cd ~/lczero_dev_portal/production
./start_gunicorn.sh
```

Test in another terminal: `curl http://127.0.0.1:8000/`

## 8. Systemd Service Configuration

### 8.1 Create systemd service file
```bash
sudo nano /etc/systemd/system/lczero-dev-portal.service
```

Add the following configuration:
```ini
[Unit]
Description=Lczero Dev Portal Django Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=lc0
Group=lc0
WorkingDirectory=/home/lc0/lczero_dev_portal/production
ExecStart=/home/lc0/lczero_dev_portal/production/start_gunicorn.sh
ExecReload=/bin/kill -s HUP $MAINPID
RestartSec=5
Restart=on-failure
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 8.2 Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable lczero-dev-portal.service
sudo systemctl start lczero-dev-portal.service
```

### 8.3 Check service status
```bash
sudo systemctl status lczero-dev-portal.service
```

### 8.4 View service logs
```bash
sudo journalctl -u lczero-dev-portal.service -f
```

## 9. Nginx Configuration

### 9.1 Create nginx site configuration
```bash
sudo nano /etc/nginx/sites-available/lczero-dev-portal
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name dev.lczero.org;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types
        application/javascript
        application/json
        text/css
        text/javascript
        text/plain
        text/xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=main:10m rate=10r/s;
    limit_req zone=main burst=20 nodelay;

    # Static files
    location /static/ {
        alias /home/lc0/lczero_dev_portal/shared/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/lc0/lczero_dev_portal/shared/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Artifacts files (with authentication check)
    location /static/artifacts/ {
        alias /home/lc0/lczero_dev_portal/shared/artifacts/;
        # Consider adding authentication here if needed
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Favicon
    location /favicon.ico {
        access_log off;
        log_not_found off;
        return 204;
    }

    # Robots.txt
    location /robots.txt {
        access_log off;
        log_not_found off;
        return 200 "User-agent: *\nDisallow: /admin/\n";
        add_header Content-Type text/plain;
    }
}
```

### 9.2 Enable the site
```bash
sudo ln -s /etc/nginx/sites-available/lczero-dev-portal /etc/nginx/sites-enabled/
```

### 9.3 Test nginx configuration
```bash
sudo nginx -t
```

### 9.4 Reload nginx
```bash
sudo systemctl reload nginx
```

## 10. SSL/HTTPS Setup (Optional but Recommended)

### 10.1 Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 10.2 Obtain SSL certificate
```bash
sudo certbot --nginx -d dev.lczero.org
```

### 10.3 Set up automatic renewal
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 11. File Permissions and Security

### 11.1 Set proper file permissions
```bash
cd ~/lczero_dev_portal
chmod -R 755 production
chmod -R 755 shared
chmod 600 production/.env
```

### 11.2 Create log rotation
```bash
sudo nano /etc/logrotate.d/lczero-dev-portal
```

Add:
```
/home/lc0/lczero_dev_portal/shared/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
    su lc0 lc0
}
```

## 12. Deployment Verification

### 12.1 Check all services are running
```bash
sudo systemctl status postgresql
sudo systemctl status lczero-dev-portal
sudo systemctl status nginx
```

### 12.2 Test the application
```bash
curl -I http://dev.lczero.org/
curl -I https://dev.lczero.org/  # If SSL is configured
```

### 12.3 Check Django admin
Visit: https://dev.lczero.org/admin/

### 12.4 Check logs for errors
```bash
tail -f ~/lczero_dev_portal/shared/logs/gunicorn_error.log
sudo journalctl -u lczero-dev-portal.service -f
sudo tail -f /var/log/nginx/error.log
```

## 13. Backup Strategy

### 13.1 Create database backup script
```bash
mkdir -p ~/lczero_dev_portal/backups
nano ~/lczero_dev_portal/backups/backup_db.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/lc0/lczero_dev_portal/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
pg_dump -h localhost -U lczero_prod lczero_dev_portal > "$BACKUP_DIR/db_backup_$DATE.sql"
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
```

Make executable and test:
```bash
chmod +x ~/lczero_dev_portal/backups/backup_db.sh
~/lczero_dev_portal/backups/backup_db.sh
```

### 13.2 Set up automated backups
```bash
crontab -e
```

Add:
```
# Daily database backup at 2 AM
0 2 * * * /home/lc0/lczero_dev_portal/backups/backup_db.sh
```

## 14. Monitoring and Maintenance

### 14.1 Create health check script
```bash
nano ~/lczero_dev_portal/health_check.sh
```

Add:
```bash
#!/bin/bash
echo "=== Health Check $(date) ==="
echo "Service status:"
systemctl is-active lczero-dev-portal.service
echo "App response:"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/
echo ""
echo "Disk usage:"
df -h | grep -E "(/$|/home)"
echo "Memory usage:"
free -m
```

Make executable:
```bash
chmod +x ~/lczero_dev_portal/health_check.sh
```

## 15. Update/Deployment Process

### 15.1 Create deployment script for updates
```bash
nano ~/lczero_dev_portal/deploy.sh
```

Add:
```bash
#!/bin/bash
set -e

echo "Starting deployment..."
cd /home/lc0/lczero_dev_portal/production

# Backup current version
echo "Backing up current version..."
git rev-parse HEAD > ../shared/previous_deployment.txt

# Pull latest changes
echo "Pulling latest changes..."
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run Django checks
echo "Running Django checks..."
cd lczero_dev_portal
python manage.py check --verbosity=2

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart the service
echo "Restarting service..."
sudo systemctl restart lczero-dev-portal.service

# Wait for service to start
sleep 5

# Check if service is running
if systemctl is-active --quiet lczero-dev-portal.service; then
    echo "Deployment successful! Service is running."
else
    echo "Deployment failed! Service is not running."
    exit 1
fi
```

Make executable:
```bash
chmod +x ~/lczero_dev_portal/deploy.sh
```

## 16. Troubleshooting Commands

### Common diagnostic commands:
```bash
# Check service logs
sudo journalctl -u lczero-dev-portal.service -n 50

# Check Gunicorn logs
tail -f ~/lczero_dev_portal/shared/logs/gunicorn_error.log

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Test Django manually
cd ~/lczero_dev_portal/production/lczero_dev_portal
source ../venv/bin/activate
python manage.py shell

# Check database connection
python manage.py dbshell

# Restart services
sudo systemctl restart lczero-dev-portal.service
sudo systemctl reload nginx
```

This completes the detailed deployment instructions for the LCZero Dev Portal.