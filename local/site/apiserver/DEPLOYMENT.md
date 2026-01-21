# Deployment Guide

Complete guide for deploying the k8s.io/apiserver documentation site.

## Deployment Options

### 1. Docker (Recommended)

#### Quick Start

```bash
# Build and run
make docker-run

# Access at http://localhost:9003
```

#### Manual Docker Commands

```bash
# Build image
docker build -t apiserver-docs:latest .

# Run container
docker run -d \
  --name apiserver-docs \
  -p 9003:9003 \
  --restart unless-stopped \
  apiserver-docs:latest

# View logs
docker logs -f apiserver-docs

# Stop and remove
docker stop apiserver-docs
docker rm apiserver-docs
```

#### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### 2. Static Hosting

#### GitHub Pages

```bash
# Build site
make build

# Deploy to gh-pages branch
cd public
git init
git add .
git commit -m "Deploy documentation"
git remote add origin <your-repo>
git push -f origin master:gh-pages
```

#### Netlify

```toml
# netlify.toml
[build]
  command = "make build"
  publish = "public"

[build.environment]
  HUGO_VERSION = "0.121.0"
```

Deploy via:
- Netlify CLI: `netlify deploy --prod`
- Git integration: Push to connected repository
- Drag & drop: Upload `public/` directory

#### Vercel

```json
{
  "buildCommand": "make build",
  "outputDirectory": "public",
  "framework": "hugo"
}
```

Deploy via:
- Vercel CLI: `vercel --prod`
- Git integration: Push to connected repository

#### AWS S3 + CloudFront

```bash
# Build site
make build

# Sync to S3
aws s3 sync public/ s3://your-bucket-name/ \
  --delete \
  --cache-control "max-age=31536000,public"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

### 3. Traditional Web Server

#### Nginx

```nginx
server {
    listen 9003;
    server_name docs.example.com;
    
    root /var/www/apiserver-docs;
    index index.html;
    
    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
    
    # Cache static assets
    location ~* \.(svg|css|js|jpg|jpeg|png|gif|ico|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # HTML files - shorter cache
    location ~* \.html$ {
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }
    
    # Handle clean URLs
    location / {
        try_files $uri $uri/ $uri.html =404;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Deploy:
```bash
# Build site
make build

# Copy to web root
sudo cp -r public/* /var/www/apiserver-docs/

# Reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### Apache

```apache
<VirtualHost *:9003>
    ServerName docs.example.com
    DocumentRoot /var/www/apiserver-docs
    
    <Directory /var/www/apiserver-docs>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # Enable compression
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json image/svg+xml
    </IfModule>
    
    # Cache control
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType image/svg+xml "access plus 1 year"
        ExpiresByType text/css "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType text/html "access plus 1 hour"
    </IfModule>
    
    # Rewrite rules for clean URLs
    <IfModule mod_rewrite.c>
        RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule ^(.*)$ $1.html [L]
    </IfModule>
</VirtualHost>
```

Deploy:
```bash
# Build site
make build

# Copy to web root
sudo cp -r public/* /var/www/apiserver-docs/

# Reload Apache
sudo apachectl configtest
sudo systemctl reload apache2
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apiserver-docs
  labels:
    app: apiserver-docs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: apiserver-docs
  template:
    metadata:
      labels:
        app: apiserver-docs
    spec:
      containers:
      - name: docs
        image: apiserver-docs:latest
        ports:
        - containerPort: 9003
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 9003
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 9003
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: apiserver-docs
spec:
  selector:
    app: apiserver-docs
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9003
  type: LoadBalancer
```

Deploy:
```bash
# Build and push image
docker build -t your-registry/apiserver-docs:latest .
docker push your-registry/apiserver-docs:latest

# Deploy to Kubernetes
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=apiserver-docs
kubectl get svc apiserver-docs
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'local/docs/apiserver/**'
      - 'local/site/apiserver/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: '0.121.0'
          extended: true
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Build site
        run: |
          cd local/site/apiserver
          make build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./local/site/apiserver/public
```

### GitLab CI

```yaml
image: python:3.11

stages:
  - build
  - deploy

variables:
  HUGO_VERSION: "0.121.0"

before_script:
  - wget https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_Linux-64bit.tar.gz
  - tar -xzf hugo_extended_${HUGO_VERSION}_Linux-64bit.tar.gz
  - mv hugo /usr/local/bin/

build:
  stage: build
  script:
    - cd local/site/apiserver
    - make build
  artifacts:
    paths:
      - local/site/apiserver/public

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

## Monitoring

### Health Checks

```bash
# HTTP health check
curl -f http://localhost:9003 || exit 1

# Docker health check (already configured in Dockerfile)
docker inspect --format='{{.State.Health.Status}}' apiserver-docs
```

### Prometheus Metrics

Add metrics endpoint (optional):

```python
# Add to a separate metrics.py
from prometheus_client import start_http_server, Counter, Gauge
import time

# Start metrics server on port 9090
start_http_server(9090)

# Define metrics
page_views = Counter('page_views_total', 'Total page views')
active_connections = Gauge('active_connections', 'Active connections')
```

### Logging

```bash
# Docker logs
docker logs -f apiserver-docs

# Docker Compose logs
docker-compose logs -f

# System logs (if using systemd)
journalctl -u apiserver-docs -f
```

## Backup and Recovery

### Backup

```bash
# Backup source documentation
tar -czf apiserver-docs-backup-$(date +%Y%m%d).tar.gz \
  ../../docs/apiserver/

# Backup built site
tar -czf apiserver-site-backup-$(date +%Y%m%d).tar.gz \
  public/
```

### Recovery

```bash
# Restore documentation
tar -xzf apiserver-docs-backup-YYYYMMDD.tar.gz

# Rebuild site
make rebuild
```

## Security

### HTTPS Configuration

#### Let's Encrypt with Nginx

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d docs.example.com

# Auto-renewal is configured automatically
```

#### Cloudflare

- Enable "Always Use HTTPS"
- Set SSL/TLS mode to "Full (strict)"
- Enable "Automatic HTTPS Rewrites"

### Security Headers

Already configured in nginx/Apache examples above:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Content-Security-Policy (optional)

## Performance Optimization

### CDN Integration

#### Cloudflare

1. Add site to Cloudflare
2. Update DNS records
3. Enable caching and optimization features

#### AWS CloudFront

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name your-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

### Compression

Already enabled in nginx/Apache configs. Verify:

```bash
curl -H "Accept-Encoding: gzip" -I http://localhost:9003
```

### Image Optimization

SVG diagrams are already optimized. For additional optimization:

```bash
# Install svgo
npm install -g svgo

# Optimize all SVGs
find static/diagrams -name "*.svg" -exec svgo {} \;
```

## Troubleshooting

### Site Not Loading

```bash
# Check if container is running
docker ps | grep apiserver-docs

# Check logs
docker logs apiserver-docs

# Check port binding
netstat -tlnp | grep 9003
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/apiserver-docs

# Fix permissions
sudo chmod -R 755 /var/www/apiserver-docs
```

### Build Failures

```bash
# Clean and rebuild
make clean
make build

# Check Hugo version
hugo version

# Verify Python version
python3 --version
```

## Rollback

### Docker

```bash
# Tag previous version
docker tag apiserver-docs:latest apiserver-docs:backup

# Rollback
docker stop apiserver-docs
docker rm apiserver-docs
docker run -d --name apiserver-docs -p 9003:9003 apiserver-docs:backup
```

### Static Files

```bash
# Restore from backup
tar -xzf apiserver-site-backup-YYYYMMDD.tar.gz
sudo cp -r public/* /var/www/apiserver-docs/
```

---

**Last Updated**: January 2026  
**Deployment Port**: 9003  
**Recommended**: Docker deployment for ease of use
