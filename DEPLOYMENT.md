# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- Ethereum RPC endpoint (Infura, Alchemy, or self-hosted)
- Solana RPC endpoint (optional, defaults to public mainnet)

## Production Deployment with Docker

### 1. Prepare Environment

```bash
# Clone repository
git clone <repository-url>
cd crypto-portfolio-tracker

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with your configuration
```

### 2. Configure Environment Variables

**Required settings in `.env`:**

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://postgres:your_secure_password@postgres:5432/crypto_portfolio

# Blockchain RPCs
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Security
API_KEY=your_secure_api_key_here
CORS_ORIGINS=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Check health
curl http://localhost:5000/api/v1/health
```

### 4. Database Migrations

Migrations run automatically on startup. To run manually:

```bash
docker-compose exec app alembic upgrade head
```

## Manual Production Deployment

### 1. System Setup

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql redis-server

# Create application user
sudo useradd -m -s /bin/bash cryptoapp
sudo su - cryptoapp
```

### 2. Application Setup

```bash
# Clone and setup
git clone <repository-url>
cd crypto-portfolio-tracker

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

### 3. Database Setup

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE crypto_portfolio;
CREATE USER cryptoapp WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE crypto_portfolio TO cryptoapp;
\q

# Run migrations
alembic upgrade head
```

### 4. Systemd Service

Create `/etc/systemd/system/crypto-portfolio.service`:

```ini
[Unit]
Description=Crypto Portfolio Tracker
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=cryptoapp
Group=cryptoapp
WorkingDirectory=/home/cryptoapp/crypto-portfolio-tracker
Environment="PATH=/home/cryptoapp/crypto-portfolio-tracker/venv/bin"
ExecStart=/home/cryptoapp/crypto-portfolio-tracker/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile /home/cryptoapp/logs/access.log \
    --error-logfile /home/cryptoapp/logs/error.log \
    app.main:app

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-portfolio
sudo systemctl start crypto-portfolio
sudo systemctl status crypto-portfolio
```

## Nginx Reverse Proxy

### 1. Install Nginx

```bash
sudo apt install nginx
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/crypto-portfolio`:

```nginx
upstream crypto_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://crypto_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /api/v1/health {
        proxy_pass http://crypto_app;
        access_log off;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/crypto-portfolio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
sudo systemctl status certbot.timer
```

## Kubernetes Deployment

### 1. Create ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: crypto-portfolio-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  SOLANA_RPC_URL: "https://api.mainnet-beta.solana.com"
```

### 2. Create Secret

```bash
kubectl create secret generic crypto-portfolio-secrets \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=ETHEREUM_RPC_URL='https://...' \
  --from-literal=API_KEY='your-secret-key'
```

### 3. Create Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-portfolio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crypto-portfolio
  template:
    metadata:
      labels:
        app: crypto-portfolio
    spec:
      containers:
      - name: app
        image: crypto-portfolio:latest
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: crypto-portfolio-config
        - secretRef:
            name: crypto-portfolio-secrets
        livenessProbe:
          httpGet:
            path: /api/v1/live
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 4. Create Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: crypto-portfolio
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 5000
  selector:
    app: crypto-portfolio
```

Deploy:

```bash
kubectl apply -f k8s/
```

## Monitoring & Logging

### 1. Application Logs

```bash
# Docker
docker-compose logs -f app

# Systemd
journalctl -u crypto-portfolio -f

# Log files
tail -f logs/app.log
tail -f logs/error.log
```

### 2. Database Monitoring

```bash
# Check connections
docker-compose exec postgres psql -U postgres -d crypto_portfolio \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Check table sizes
docker-compose exec postgres psql -U postgres -d crypto_portfolio \
  -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables WHERE schemaname = 'public';"
```

### 3. Redis Monitoring

```bash
# Check Redis stats
docker-compose exec redis redis-cli INFO stats

# Monitor commands
docker-compose exec redis redis-cli MONITOR
```

## Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres crypto_portfolio > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres crypto_portfolio < backup.sql
```

### Automated Backups

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * docker-compose exec -T postgres pg_dump -U postgres crypto_portfolio | gzip > /backups/crypto_portfolio_$(date +\%Y\%m\%d).sql.gz

# Keep last 7 days
0 3 * * * find /backups -name "crypto_portfolio_*.sql.gz" -mtime +7 -delete
```

## Scaling

### Horizontal Scaling

```bash
# Scale app instances
docker-compose up -d --scale app=3
```

### Load Balancing

Use Nginx or HAProxy to distribute traffic across multiple instances.

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Set strong API_KEY
- [ ] Enable HTTPS with valid certificate
- [ ] Configure firewall (UFW/iptables)
- [ ] Set up rate limiting
- [ ] Restrict CORS origins
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Set up intrusion detection (fail2ban)
- [ ] Regular backups with encryption

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs app

# Check database connection
docker-compose exec postgres psql -U postgres -c "SELECT 1;"

# Verify environment variables
docker-compose exec app env | grep DATABASE_URL
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Reduce worker count in gunicorn
# Edit docker-compose.yml: --workers 2
```

### Slow Response Times

- Check database query performance
- Verify Redis cache is working
- Monitor blockchain RPC latency
- Consider adding more workers
- Enable connection pooling

## Performance Tuning

### PostgreSQL

```sql
-- Analyze tables
ANALYZE;

-- Create indexes
CREATE INDEX idx_balances_wallet_id ON balances(wallet_id);
CREATE INDEX idx_balance_history_wallet_recorded ON balance_history(wallet_id, recorded_at DESC);
```

### Redis

```bash
# Increase max memory
docker-compose exec redis redis-cli CONFIG SET maxmemory 512mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Application

- Increase gunicorn workers: `--workers $(nproc)`
- Enable database connection pooling
- Tune cache TTL values
- Implement request batching
