# Docker Setup Guide

This document explains the Docker-based build and deployment setup for the client-go documentation site.

## Overview

The site now uses a **Docker-first approach** where all build tools and dependencies are containerized. This means you only need Docker installed - no need for Hugo, Python, mermaid-cli, or other tools locally.

## Architecture

### Multi-Stage Dockerfile

The `Dockerfile` uses a two-stage build:

**Stage 1: Builder** (node:18-alpine)
- Installs Hugo, Python, mermaid-cli, and Chromium
- Processes markdown content
- Converts Mermaid diagrams to SVG
- Builds the site with Hugo

**Stage 2: Runtime** (python:3.9-slim-buster)
- Copies only the built site from Stage 1
- Serves with Python HTTP server
- Minimal image size (~150 MB vs ~1 GB)

### Directory Structure

```
client-go/
├── scripts/              # Build scripts (used in Docker)
│   ├── process_mermaid.py
│   ├── process_content.py
│   ├── build.sh
│   ├── serve.sh
│   └── README.md
├── Dockerfile            # Multi-stage build
├── docker-compose.yml    # Orchestration
├── Makefile             # Convenience commands
└── [other files]
```

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# One command to build and run
make quick-docker

# Or directly with docker-compose
docker-compose up -d --build

# Visit http://localhost:9002
```

### Option 2: Docker CLI

```bash
# Build the image
docker build -t client-go-docs:latest .

# Run the container
docker run -d \
  --name client-go-docs \
  -p 9002:9002 \
  --restart unless-stopped \
  client-go-docs:latest

# Visit http://localhost:9002
```

### Option 3: Makefile

```bash
# Build Docker image
make docker-build

# Run container
make docker-run

# Stop container
make docker-stop
```

## What Happens During Build

1. **Base Image**: Starts with `node:18-alpine` (includes Node.js and npm)

2. **Install Dependencies**:
   ```dockerfile
   RUN apk add --no-cache hugo python3 py3-pip chromium chromium-chromedriver
   RUN npm install -g @mermaid-js/mermaid-cli
   ```

3. **Copy Source Files**:
   ```dockerfile
   COPY . .
   ```

4. **Process Content**:
   ```dockerfile
   RUN python3 scripts/process_mermaid.py
   ```
   - Fixes markdown links
   - Converts 23 Mermaid diagrams to SVG
   - Generates content files

5. **Build Site**:
   ```dockerfile
   RUN hugo --minify
   ```
   - Generates static HTML
   - Minifies assets
   - Creates `public/` directory

6. **Runtime Stage**:
   ```dockerfile
   FROM python:3.9-slim-buster
   COPY --from=builder /build/public .
   CMD ["python3", "-m", "http.server", "9002"]
   ```
   - Copies only built site
   - Serves on port 9002

## Build Time

- **First build**: ~5-10 minutes (downloads base images, installs dependencies)
- **Subsequent builds**: ~2-3 minutes (uses cached layers)
- **Content-only changes**: ~1-2 minutes (only rebuilds from content step)

## Image Sizes

- **Builder stage**: ~1 GB (includes Hugo, Node.js, Chromium)
- **Final image**: ~150 MB (only Python + built site)
- **Built site**: ~1.4 MB

## Docker Compose Configuration

```yaml
version: '3.8'

services:
  client-go-docs:
    build:
      context: .
      dockerfile: Dockerfile
    image: client-go-docs:latest
    container_name: client-go-docs
    ports:
      - "9002:9002"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:9002')"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

## Makefile Commands

### Docker Commands

```bash
make docker-build          # Build Docker image
make docker-run            # Run container
make docker-stop           # Stop and remove container
make docker-clean          # Remove image and container
make docker-logs           # View container logs
make docker-shell          # Open shell in container
```

### Docker Compose Commands

```bash
make docker-compose-up     # Start services
make docker-compose-down   # Stop services
make docker-compose-logs   # View logs
make docker-compose-rebuild # Rebuild and restart
make quick-docker          # Quick start (recommended)
```

## Environment Variables

You can customize the build with environment variables:

```bash
# Change port
PORT=8080 docker-compose up -d

# Or in Makefile
make docker-run PORT=8080
```

## Health Checks

The container includes a health check that runs every 30 seconds:

```bash
# Check container health
docker ps

# View health check logs
docker inspect client-go-docs | grep -A 10 Health
```

## Logs

View container logs:

```bash
# Follow logs
docker-compose logs -f

# Or with Docker CLI
docker logs -f client-go-docs

# Or with Makefile
make docker-logs
```

## Updating Content

When you update the source documentation:

```bash
# Rebuild and restart
make docker-compose-rebuild

# Or
docker-compose up -d --build
```

## Troubleshooting

### Build Fails

```bash
# Clean everything and rebuild
docker-compose down
docker system prune -f
docker-compose up -d --build
```

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check if port is in use
lsof -i :9002

# Try different port
PORT=9003 docker-compose up -d
```

### SVG Conversion Fails

The Dockerfile includes Chromium for mermaid-cli. If SVG conversion fails:

```bash
# Check builder logs
docker-compose logs | grep mermaid

# Rebuild without cache
docker-compose build --no-cache
```

### Out of Disk Space

```bash
# Clean up Docker
docker system prune -a -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f
```

## Production Deployment

### Build for Production

```bash
# Build optimized image
docker build \
  --tag client-go-docs:1.0.0 \
  --tag client-go-docs:latest \
  .
```

### Run in Production

```bash
# Run with restart policy
docker run -d \
  --name client-go-docs \
  -p 9002:9002 \
  --restart always \
  --memory 256m \
  --cpus 0.5 \
  client-go-docs:latest
```

### Push to Registry

```bash
# Tag for registry
docker tag client-go-docs:latest your-registry.com/client-go-docs:latest

# Push
docker push your-registry.com/client-go-docs:latest
```

## Advantages of Docker Approach

1. **No Local Dependencies**: Only Docker required
2. **Consistent Builds**: Same environment everywhere
3. **Easy Deployment**: Single container to deploy
4. **Isolated Environment**: No conflicts with local tools
5. **Reproducible**: Same result every time
6. **Easy Updates**: Just rebuild the image

## Comparison: Local vs Docker

| Aspect | Local Build | Docker Build |
|--------|-------------|--------------|
| Prerequisites | Hugo, Python, mermaid-cli, Node.js | Docker only |
| Setup Time | 15-30 minutes | 2 minutes |
| Build Time | 30 seconds | 2-3 minutes (first: 5-10 min) |
| Consistency | Varies by system | Always same |
| Deployment | Manual setup | Single container |
| Updates | Update each tool | Rebuild image |

## Best Practices

1. **Use Docker Compose** for local development
2. **Use multi-stage builds** to minimize image size
3. **Pin base image versions** for reproducibility
4. **Use .dockerignore** to exclude unnecessary files
5. **Add health checks** for production
6. **Set resource limits** in production
7. **Use volumes** for persistent data (if needed)
8. **Monitor logs** regularly

## Scripts in Docker

All scripts in the `scripts/` folder are used during the Docker build:

- `process_mermaid.py`: Main content processor
- `process_content.py`: Legacy (kept for reference)
- `build.sh`: Shell build script
- `serve.sh`: Shell serve script

These scripts are executed inside the container during build, so you don't need to run them manually when using Docker.

## Summary

The Docker setup provides a complete, self-contained build and deployment solution:

✅ **One command to run**: `make quick-docker`  
✅ **No local dependencies**: Only Docker needed  
✅ **Consistent builds**: Same everywhere  
✅ **Production ready**: Includes health checks  
✅ **Easy updates**: Rebuild and restart  

For most users, the Docker approach is recommended over local builds.

---

**Updated**: January 15, 2026  
**Docker Version**: 20.10+  
**Docker Compose Version**: 2.0+
