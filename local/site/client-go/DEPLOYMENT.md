# Deployment Guide

This guide covers different ways to deploy the client-go documentation site.

## Quick Start

### Local Development

```bash
# Start Hugo development server with live reload
hugo server -D

# Visit http://localhost:1313
```

### Production Build

```bash
# Build everything
./build.sh

# Serve with Python
cd public && python3 -m http.server 9002

# Visit http://localhost:9002
```

## Docker Deployment

### Option 1: Docker CLI

```bash
# Build the site
hugo --minify

# Build Docker image
docker build -t client-go-docs:latest .

# Run container
docker run -d \
  --name client-go-docs \
  -p 9002:9002 \
  --restart unless-stopped \
  client-go-docs:latest

# Check logs
docker logs client-go-docs

# Stop and remove
docker stop client-go-docs
docker rm client-go-docs
```

### Option 2: Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Option 3: Build Script with Docker

```bash
# Build site and Docker image in one command
./build.sh --docker

# Run the container
docker run -d -p 9002:9002 --name client-go-docs client-go-docs:latest
```

## Kubernetes Deployment

### Basic Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: client-go-docs
  namespace: documentation
spec:
  replicas: 2
  selector:
    matchLabels:
      app: client-go-docs
  template:
    metadata:
      labels:
        app: client-go-docs
    spec:
      containers:
      - name: docs
        image: client-go-docs:latest
        ports:
        - containerPort: 9002
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
            port: 9002
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 9002
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: client-go-docs
  namespace: documentation
spec:
  selector:
    app: client-go-docs
  ports:
  - port: 80
    targetPort: 9002
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: client-go-docs
  namespace: documentation
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - client-go-docs.example.com
    secretName: client-go-docs-tls
  rules:
  - host: client-go-docs.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: client-go-docs
            port:
              number: 80
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

## Static Hosting

### GitHub Pages

1. Build the site:
   ```bash
   hugo --minify
   ```

2. Push `public/` directory to `gh-pages` branch:
   ```bash
   cd public
   git init
   git add .
   git commit -m "Deploy site"
   git remote add origin https://github.com/yourusername/client-go-docs.git
   git push -f origin master:gh-pages
   ```

3. Enable GitHub Pages in repository settings

### Netlify

1. Create `netlify.toml`:
   ```toml
   [build]
     publish = "public"
     command = "hugo --minify"

   [context.production.environment]
     HUGO_VERSION = "0.154.5"
     HUGO_ENV = "production"
   ```

2. Connect repository to Netlify
3. Deploy automatically on push

### AWS S3 + CloudFront

```bash
# Build site
hugo --minify

# Sync to S3
aws s3 sync public/ s3://your-bucket-name/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Nginx Deployment

### Option 1: Direct Nginx

```nginx
# /etc/nginx/sites-available/client-go-docs
server {
    listen 80;
    server_name client-go-docs.example.com;
    
    root /var/www/client-go-docs;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Deploy:

```bash
# Build site
hugo --minify

# Copy to web root
sudo cp -r public/* /var/www/client-go-docs/

# Enable site
sudo ln -s /etc/nginx/sites-available/client-go-docs /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Nginx + Docker

```yaml
# docker-compose.yml with Nginx
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./public:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Documentation

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: '0.154.5'
          extended: true
      
      - name: Process content
        run: |
          cd local/site/client-go
          python3 process_content.py
      
      - name: Build site
        run: |
          cd local/site/client-go
          hugo --minify
      
      - name: Build and push Docker image
        run: |
          cd local/site/client-go
          docker build -t ghcr.io/${{ github.repository }}/client-go-docs:latest .
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/${{ github.repository }}/client-go-docs:latest
```

## Monitoring

### Health Check Endpoint

The Python HTTP server doesn't have a dedicated health check endpoint, but you can check the root:

```bash
curl -f http://localhost:9002/ || exit 1
```

### Prometheus Metrics

For production deployments, consider using a proper web server with metrics:

```yaml
# Use Nginx with prometheus exporter
services:
  nginx:
    image: nginx:alpine
    # ... nginx config ...
  
  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    ports:
      - "9113:9113"
    command:
      - -nginx.scrape-uri=http://nginx:80/stub_status
```

## Performance Optimization

### Enable Compression

Already enabled in Hugo build with `--minify` flag.

### CDN Integration

For production, serve static assets via CDN:

1. Upload `public/` to CDN
2. Update `baseURL` in `hugo.toml`
3. Rebuild site

### Caching Headers

Add to Nginx config:

```nginx
location / {
    add_header Cache-Control "public, max-age=3600";
}

location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

## Security

### HTTPS

Always use HTTPS in production:

```bash
# With Let's Encrypt
sudo certbot --nginx -d client-go-docs.example.com
```

### Security Headers

Add to Nginx config:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 9002
lsof -i :9002

# Kill process
kill -9 <PID>
```

### Docker Build Fails

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t client-go-docs:latest .
```

### Site Not Loading

1. Check if server is running:
   ```bash
   curl http://localhost:9002
   ```

2. Check Docker logs:
   ```bash
   docker logs client-go-docs
   ```

3. Verify files exist:
   ```bash
   ls -la public/
   ```

## Updating the Site

```bash
# 1. Update markdown files in ../../docs/client-go/

# 2. Regenerate content
python3 process_content.py

# 3. Rebuild site
hugo --minify

# 4. Rebuild Docker image (if using Docker)
docker build -t client-go-docs:latest .

# 5. Restart container
docker stop client-go-docs
docker rm client-go-docs
docker run -d -p 9002:9002 --name client-go-docs client-go-docs:latest
```

Or use the build script:

```bash
./build.sh --docker
docker restart client-go-docs
```

## Backup and Restore

### Backup

```bash
# Backup source files
tar -czf client-go-docs-backup-$(date +%Y%m%d).tar.gz \
  content/ themes/ static/ hugo.toml

# Backup built site
tar -czf client-go-docs-public-$(date +%Y%m%d).tar.gz public/
```

### Restore

```bash
# Restore source
tar -xzf client-go-docs-backup-YYYYMMDD.tar.gz

# Rebuild
hugo --minify
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/kubernetes/kubernetes/issues
- Kubernetes Slack: #client-go channel
