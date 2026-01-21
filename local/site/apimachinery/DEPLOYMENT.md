# Deployment Guide

## Quick Start

### Option 1: Hugo Development Server (Recommended for Development)

```bash
cd /Users/adamz/work/k8s/kubernetes/local/site/apimachinery
hugo server --port 9001
```

Visit: http://localhost:9001

### Option 2: Python HTTP Server

```bash
cd /Users/adamz/work/k8s/kubernetes/local/site/apimachinery
hugo --minify
cd public
python3 -m http.server 9001
```

Visit: http://localhost:9001

### Option 3: Docker (Recommended for Production)

```bash
cd /Users/adamz/work/k8s/kubernetes/local/site/apimachinery
./build-and-run.sh
```

Or manually:

```bash
# Build site
hugo --minify

# Build Docker image
docker build -t apimachinery-docs:latest .

# Run container
docker run -d -p 9001:9001 --name apimachinery-docs apimachinery-docs:latest
```

Visit: http://localhost:9001

## Features Implemented

### ✅ Light/Dark Mode Toggle
- Click the theme toggle button (🌙/☀️) in the top right
- Preference is saved in localStorage
- Automatic theme detection based on system preferences

### ✅ Collapsible Sidebar Menu
- Click the hamburger menu icon to collapse/expand
- State is saved in localStorage
- Tooltips show on hover

### ✅ Resizable Sidebar
- Drag the resize handle between sidebar and content
- Width is saved in localStorage
- Min width: 200px, Max width: 600px

### ✅ Navigation
- All pages are linked in the sidebar menu
- Previous/Next navigation at bottom of pages
- Active page is highlighted

### ✅ SVG Diagrams
- Mermaid diagrams are converted to SVG
- Hash-based filenames for caching
- Responsive sizing

### ✅ Responsive Design
- Mobile-friendly layout
- Adaptive sidebar behavior
- Touch-friendly controls

## File Structure

```
local/site/apimachinery/
├── archetypes/              # Hugo content templates
├── content/                 # Markdown content (generated from docs)
│   ├── _index.md           # Home page
│   ├── 00-overview.md
│   ├── 01-runtime-package.md
│   ├── 02-api-meta-package.md
│   ├── 03-labels-and-fields-packages.md
│   ├── 04-watch-package.md
│   ├── 05-serialization.md
│   ├── 06-utility-packages.md
│   └── 07-conversion-and-resources.md
├── themes/
│   └── apimachinery-theme/
│       ├── layouts/
│       │   ├── _default/
│       │   │   ├── baseof.html      # Base template
│       │   │   ├── single.html      # Single page
│       │   │   └── list.html        # List page
│       │   ├── partials/
│       │   │   └── menu.html        # Menu partial
│       │   └── index.html           # Home page
│       ├── static/
│       │   ├── css/
│       │   │   └── style.css        # Main stylesheet
│       │   └── js/
│       │       ├── theme.js         # Theme toggle
│       │       ├── menu.js          # Menu collapse
│       │       └── resize.js        # Sidebar resize
│       └── theme.toml
├── static/
│   └── diagrams/                    # Generated SVG diagrams
│       ├── diagram-*.svg            # SVG files
│       └── diagram-*.mmd            # Mermaid source
├── public/                          # Generated site (gitignored)
├── hugo.toml                        # Hugo configuration
├── convert_mermaid.py               # Documentation processor
├── Dockerfile                       # Docker configuration
├── .dockerignore                    # Docker ignore file
├── build-and-run.sh                 # Build and run script
├── README.md                        # User documentation
└── DEPLOYMENT.md                    # This file
```

## Docker Commands

### Build Image
```bash
docker build -t apimachinery-docs:latest .
```

### Run Container
```bash
docker run -d -p 9001:9001 --name apimachinery-docs apimachinery-docs:latest
```

### View Logs
```bash
docker logs apimachinery-docs
docker logs -f apimachinery-docs  # Follow logs
```

### Stop Container
```bash
docker stop apimachinery-docs
```

### Remove Container
```bash
docker rm apimachinery-docs
```

### Restart Container
```bash
docker restart apimachinery-docs
```

### Shell into Container
```bash
docker exec -it apimachinery-docs /bin/bash
```

## Updating Documentation

When documentation in `../../docs/apimachinery` is updated:

1. **Regenerate content:**
   ```bash
   cd /Users/adamz/work/k8s/kubernetes/local/site/apimachinery
   python3 convert_mermaid.py
   ```

2. **Rebuild site:**
   ```bash
   hugo --minify
   ```

3. **Rebuild Docker image (if using Docker):**
   ```bash
   docker build -t apimachinery-docs:latest .
   docker stop apimachinery-docs
   docker rm apimachinery-docs
   docker run -d -p 9001:9001 --name apimachinery-docs apimachinery-docs:latest
   ```

Or use the convenience script:
```bash
./build-and-run.sh
```

## Generating Actual Mermaid SVGs

The conversion script creates placeholder SVGs. To generate actual diagrams:

### Install mermaid-cli
```bash
npm install -g @mermaid-js/mermaid-cli
```

### Convert All Diagrams
```bash
cd static/diagrams
for f in *.mmd; do 
    mmdc -i "$f" -o "${f%.mmd}.svg" --theme default --backgroundColor transparent
done
```

### Rebuild Site
```bash
cd ../..
hugo --minify
```

## Customization

### Change Theme Colors

Edit `themes/apimachinery-theme/static/css/style.css`:

```css
:root {
    --bg-color: #ffffff;
    --text-color: #333333;
    --link-color: #0066cc;
    /* ... more variables */
}

[data-theme="dark"] {
    --bg-color: #1e1e1e;
    --text-color: #e0e0e0;
    /* ... dark mode overrides */
}
```

### Change Site Title

Edit `hugo.toml`:

```toml
title = 'Your Custom Title'
```

### Change Port

For Hugo server:
```bash
hugo server --port YOUR_PORT
```

For Docker:
```bash
docker run -d -p YOUR_PORT:9001 --name apimachinery-docs apimachinery-docs:latest
```

To change the internal port, edit `Dockerfile`:
```dockerfile
EXPOSE YOUR_PORT
CMD ["python3", "-m", "http.server", "YOUR_PORT"]
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 9001
lsof -i :9001

# Kill the process
kill -9 <PID>

# Or use a different port
hugo server --port 9002
```

### Docker Build Fails

```bash
# Clean up Docker
docker system prune -a

# Rebuild
docker build --no-cache -t apimachinery-docs:latest .
```

### Site Not Loading

1. Check if server is running:
   ```bash
   curl http://localhost:9001
   ```

2. Check Docker logs:
   ```bash
   docker logs apimachinery-docs
   ```

3. Verify public directory exists:
   ```bash
   ls -la public/
   ```

### Mermaid Diagrams Not Showing

1. Check if SVG files exist:
   ```bash
   ls static/diagrams/
   ```

2. Verify Hugo is copying static files:
   ```bash
   ls public/diagrams/
   ```

3. Check browser console for errors

## Performance Optimization

### Enable Caching

Add to `hugo.toml`:
```toml
[caches]
  [caches.getjson]
    dir = ":cacheDir/:project"
    maxAge = "1h"
```

### Minify Output

Already enabled in build command:
```bash
hugo --minify
```

### Compress Assets

For production, use nginx or similar with gzip:
```nginx
gzip on;
gzip_types text/css application/javascript image/svg+xml;
```

## Production Deployment

### Using Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  apimachinery-docs:
    build: .
    ports:
      - "9001:9001"
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

### Using Kubernetes

Create deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apimachinery-docs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: apimachinery-docs
  template:
    metadata:
      labels:
        app: apimachinery-docs
    spec:
      containers:
      - name: apimachinery-docs
        image: apimachinery-docs:latest
        ports:
        - containerPort: 9001
---
apiVersion: v1
kind: Service
metadata:
  name: apimachinery-docs
spec:
  selector:
    app: apimachinery-docs
  ports:
  - port: 80
    targetPort: 9001
  type: LoadBalancer
```

## License

Apache License 2.0

