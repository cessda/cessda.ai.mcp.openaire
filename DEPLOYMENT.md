# MCP OpenAIRE Server - Deployment Guide

This guide covers deploying the MCP OpenAIRE server on a server using virtualenv.

## Table of Contents

- [Server Deployment with Virtualenv](#server-deployment-with-virtualenv)
- [Running as a Systemd Service](#running-as-a-systemd-service)
- [Nginx Reverse Proxy](#nginx-reverse-proxy)
- [SSL/TLS Setup](#ssltls-setup)
- [Monitoring and Logs](#monitoring-and-logs)

## Server Deployment with Virtualenv

### 1. Prerequisites

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python 3.10+ and virtualenv
sudo apt install python3.10 python3.10-venv python3-pip -y

# Verify Python version
python3 --version  # Should be 3.10 or higher
```

### 2. Setup Project Directory

```bash
# Create application directory
sudo mkdir -p /opt/mcp-openaire
sudo chown $USER:$USER /opt/mcp-openaire
cd /opt/mcp-openaire

# Clone or copy your project
# Option 1: Clone from git
git clone https://github.com/yourusername/mcp-openaire.git .

# Option 2: Copy from local machine (run on your local machine)
# scp -r MCP_OpenAIRE/* user@your-server:/opt/mcp-openaire/
```

### 3. Create and Activate Virtual Environment

```bash
cd /opt/mcp-openaire

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 4. Install the Package

```bash
# Install in development mode (if you plan to modify code)
pip install -e .

# OR install in production mode
pip install .

# Verify installation
mcp-openaire-http --help
```

### 5. Configure Environment Variables

```bash
# Create .env file from example
cp .env.http.example .env

# Edit configuration
nano .env
```

Edit `.env` with your settings:
```bash
# OpenAIRE API Configuration
OPENAIRE_SCHOLEXPLORER_URL=https://api.scholexplorer.openaire.eu/v3
OPENAIRE_GRAPH_URL=https://api.openaire.eu/graph/v2
OPENAIRE_API_TIMEOUT=30
OPENAIRE_API_MAX_RETRIES=3

# Logging Configuration
OPENAIRE_LOG_LEVEL=INFO

# Search Parameters
OPENAIRE_DEFAULT_LIMIT=200
OPENAIRE_MAX_LIMIT=1000
OPENAIRE_PAGE_SIZE=50

# HTTP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

### 6. Test the Server

```bash
# Activate virtualenv if not already active
source venv/bin/activate

# Test API integration
python test_api.py

# Test HTTP server (foreground)
python -m mcp_openaire.server_http
```

Open another terminal and test:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"mcp-openaire","version":"0.1.0"}
```

Press `Ctrl+C` to stop the server.

## Running as a Systemd Service

### 1. Create Service User

```bash
# Create dedicated user for the service
sudo useradd -r -s /bin/false mcp-openaire

# Change ownership of the application directory
sudo chown -R mcp-openaire:mcp-openaire /opt/mcp-openaire
```

### 2. Create Systemd Service File

```bash
sudo nano /etc/systemd/system/mcp-openaire.service
```

Add the following content:

```ini
[Unit]
Description=MCP OpenAIRE Research Graph Server
After=network.target

[Service]
Type=simple
User=mcp-openaire
Group=mcp-openaire
WorkingDirectory=/opt/mcp-openaire
Environment="PATH=/opt/mcp-openaire/venv/bin"
EnvironmentFile=/opt/mcp-openaire/.env
ExecStart=/opt/mcp-openaire/venv/bin/python -m mcp_openaire.server_http

# Restart policy
Restart=on-failure
RestartSec=5s

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-openaire

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/mcp-openaire

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable mcp-openaire

# Start the service
sudo systemctl start mcp-openaire

# Check status
sudo systemctl status mcp-openaire

# View logs
sudo journalctl -u mcp-openaire -f
```

### 4. Service Management Commands

```bash
# Start service
sudo systemctl start mcp-openaire

# Stop service
sudo systemctl stop mcp-openaire

# Restart service
sudo systemctl restart mcp-openaire

# Check status
sudo systemctl status mcp-openaire

# View logs (last 100 lines)
sudo journalctl -u mcp-openaire -n 100

# View logs (follow)
sudo journalctl -u mcp-openaire -f

# View logs (today only)
sudo journalctl -u mcp-openaire --since today
```

## Nginx Reverse Proxy

### 1. Install Nginx

```bash
sudo apt install nginx -y
```

### 2. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/mcp-openaire
```

Add the following:

```nginx
server {
    listen 80;
    server_name openaire.yourdomain.com;

    # Access logs
    access_log /var/log/nginx/mcp-openaire-access.log;
    error_log /var/log/nginx/mcp-openaire-error.log;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;

        # WebSocket/SSE support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE-specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

### 3. Enable Site and Restart Nginx

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/mcp-openaire /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### 4. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Or if using specific ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

## SSL/TLS Setup

### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtain SSL Certificate

```bash
# Get certificate and auto-configure Nginx
sudo certbot --nginx -d openaire.yourdomain.com

# Follow the prompts to:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: yes)
```

### 3. Auto-Renewal Setup

```bash
# Test renewal process
sudo certbot renew --dry-run

# Certbot automatically sets up a systemd timer for renewal
# Verify it's enabled
sudo systemctl status certbot.timer
```

### 4. Updated Nginx Configuration (after SSL)

Certbot will automatically update your config, but it should look like:

```nginx
server {
    listen 80;
    server_name openaire.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name openaire.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/openaire.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/openaire.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... rest of configuration from above ...
}
```

## Monitoring and Logs

### 1. View Application Logs

```bash
# Systemd journal logs
sudo journalctl -u mcp-openaire -f

# Structured JSON logs (if redirecting to file)
tail -f /var/log/mcp-openaire/app.log | jq .
```

### 2. Monitor Service Status

```bash
# Service status
sudo systemctl status mcp-openaire

# Check if process is running
ps aux | grep mcp-openaire

# Check listening ports
sudo netstat -tlnp | grep 8000
# or
sudo ss -tlnp | grep 8000
```

### 3. Monitor System Resources

```bash
# CPU and memory usage
top
# or
htop

# Specific to MCP process
ps aux | grep mcp-openaire
```

### 4. Health Check Monitoring

Create a simple monitoring script:

```bash
nano /opt/mcp-openaire/check_health.sh
```

```bash
#!/bin/bash

HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): MCP OpenAIRE is healthy"
    exit 0
else
    echo "$(date): MCP OpenAIRE health check failed (HTTP $RESPONSE)"
    # Restart service
    sudo systemctl restart mcp-openaire
    exit 1
fi
```

```bash
chmod +x /opt/mcp-openaire/check_health.sh

# Add to crontab for periodic checks (every 5 minutes)
crontab -e

# Add line:
*/5 * * * * /opt/mcp-openaire/check_health.sh >> /var/log/mcp-openaire-health.log 2>&1
```

## Updating the Application

### 1. Pull Latest Changes

```bash
cd /opt/mcp-openaire
sudo -u mcp-openaire git pull origin main
```

### 2. Update Virtual Environment

```bash
# Switch to service user (if needed)
sudo -u mcp-openaire bash

# Activate virtualenv
source venv/bin/activate

# Update dependencies
pip install --upgrade -e .

# Exit service user shell
exit
```

### 3. Restart Service

```bash
sudo systemctl restart mcp-openaire
sudo systemctl status mcp-openaire
```

## Backup and Restore

### 1. Backup Configuration

```bash
# Create backup directory
sudo mkdir -p /opt/backups/mcp-openaire

# Backup .env file
sudo cp /opt/mcp-openaire/.env /opt/backups/mcp-openaire/.env.$(date +%Y%m%d)

# Backup entire application (optional)
sudo tar -czf /opt/backups/mcp-openaire/mcp-openaire-$(date +%Y%m%d).tar.gz \
    /opt/mcp-openaire \
    --exclude=/opt/mcp-openaire/venv \
    --exclude=/opt/mcp-openaire/__pycache__
```

### 2. Restore from Backup

```bash
# Stop service
sudo systemctl stop mcp-openaire

# Restore .env
sudo cp /opt/backups/mcp-openaire/.env.20250101 /opt/mcp-openaire/.env

# Restore full application (if needed)
sudo tar -xzf /opt/backups/mcp-openaire/mcp-openaire-20250101.tar.gz -C /

# Restart service
sudo systemctl start mcp-openaire
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status mcp-openaire

# Check logs for errors
sudo journalctl -u mcp-openaire -n 50

# Check if port is already in use
sudo netstat -tlnp | grep 8000

# Verify virtualenv and Python
/opt/mcp-openaire/venv/bin/python --version

# Test manually
sudo -u mcp-openaire /opt/mcp-openaire/venv/bin/python -m mcp_openaire.server_http
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R mcp-openaire:mcp-openaire /opt/mcp-openaire

# Fix permissions
sudo chmod -R 755 /opt/mcp-openaire
sudo chmod 600 /opt/mcp-openaire/.env
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process (replace PID)
sudo kill -9 PID

# Or change port in .env
nano /opt/mcp-openaire/.env
# Change MCP_PORT=8001

# Restart service
sudo systemctl restart mcp-openaire
```

### Memory Issues

```bash
# Check memory usage
free -h

# Add swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Security Considerations

### 1. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Fail2Ban (Optional)

```bash
# Install fail2ban
sudo apt install fail2ban -y

# Create Nginx jail
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/mcp-openaire-error.log
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban
```

### 3. Regular Updates

```bash
# Create update script
nano /opt/mcp-openaire/update.sh
```

```bash
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

```bash
chmod +x /opt/mcp-openaire/update.sh

# Run weekly via cron
sudo crontab -e
# Add: 0 2 * * 0 /opt/mcp-openaire/update.sh >> /var/log/system-updates.log 2>&1
```

## Production Checklist

- [ ] Virtual environment created and activated
- [ ] Package installed in virtualenv
- [ ] .env file configured with production settings
- [ ] API integration tested successfully
- [ ] Systemd service created and enabled
- [ ] Service starts automatically on boot
- [ ] Nginx reverse proxy configured
- [ ] SSL/TLS certificate installed
- [ ] Firewall rules configured
- [ ] Health check monitoring set up
- [ ] Log rotation configured
- [ ] Backup strategy in place
- [ ] Update procedure documented

## Support

For issues or questions:
- Check logs: `sudo journalctl -u mcp-openaire -f`
- Test APIs manually: `python test_api.py`
- Verify configuration: `cat /opt/mcp-openaire/.env`
- Check service status: `sudo systemctl status mcp-openaire`
