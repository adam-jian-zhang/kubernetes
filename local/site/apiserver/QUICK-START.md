# Quick Start Guide

Get the k8s.io/apiserver documentation site running in under 5 minutes.

## Prerequisites

Choose one of these options:

### Option 1: Docker (Easiest)
- Docker installed
- No other dependencies needed

### Option 2: Local Development
- Hugo (v0.121.0+)
- Python 3.11+
- (Optional) mermaid-cli for SVG generation

## Quick Start

### Using Docker (Recommended)

```bash
# 1. Navigate to the site directory
cd local/site/apiserver

# 2. Build and run
make docker-run

# 3. Open browser
open http://localhost:9003
```

That's it! The site is now running.

### Using Hugo Directly

```bash
# 1. Navigate to the site directory
cd local/site/apiserver

# 2. Process documentation and build
make build

# 3. Serve locally
make serve

# 4. Open browser
open http://localhost:9003
```

## What's Included

✅ **19 documentation pages** covering all apiserver packages  
✅ **110 SVG diagrams** converted from Mermaid  
✅ **Light/dark mode** toggle  
✅ **Collapsible menu** with tooltips  
✅ **Adjustable sidebar** width  
✅ **Responsive design** for mobile/tablet/desktop

## Features to Try

### 1. Toggle Dark Mode
Click the 🌙 icon in the sidebar header to switch themes.

### 2. Collapse Menu
Click the ☰ icon to collapse the sidebar to icon-only mode. Hover over icons for tooltips.

### 3. Resize Sidebar
Drag the vertical divider between the sidebar and content to adjust width.

### 4. Navigate Documentation
Click any page in the sidebar to view its content. Use Previous/Next links at the bottom of pages.

## Common Commands

```bash
# Build the site
make build

# Start development server
make serve

# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Stop Docker container
make docker-stop

# View Docker logs
make docker-logs

# Clean generated files
make clean

# Rebuild from scratch
make rebuild
```

## Directory Structure

```
apiserver/
├── public/              # Built site (after 'make build')
├── content/             # Generated Hugo content
├── static/diagrams/     # SVG diagrams (110 files)
├── themes/              # Custom theme
├── hugo.toml            # Hugo configuration
├── process_docs.py      # Documentation processor
├── Dockerfile           # Docker image
├── Makefile             # Build automation
└── README.md            # Full documentation
```

## Troubleshooting

### Port 9003 Already in Use

```bash
# Use a different port
hugo server --port 8080

# Or find and kill the process
lsof -ti:9003 | xargs kill -9
```

### Docker Build Fails

```bash
# Ensure site is built first
make build

# Then build Docker image
docker build -t apiserver-docs .
```

### Mermaid Diagrams Not Rendering

The site works without mermaid-cli (uses fallback SVGs). For proper diagrams:

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Rebuild
make clean
make build
```

### Hugo Not Found

Install Hugo:

```bash
# macOS
brew install hugo

# Linux
wget https://github.com/gohugoio/hugo/releases/download/v0.121.0/hugo_extended_0.121.0_Linux-64bit.tar.gz
tar -xzf hugo_extended_0.121.0_Linux-64bit.tar.gz
sudo mv hugo /usr/local/bin/

# Windows
choco install hugo-extended
```

## Next Steps

1. **Explore Documentation**: Browse all 19 pages covering apiserver packages
2. **Customize Theme**: Edit `themes/apiserver-theme/static/css/style.css`
3. **Deploy**: See `DEPLOYMENT.md` for production deployment options
4. **Update Content**: Edit markdown files in `../../docs/apiserver/` and rebuild

## Getting Help

- **Full Documentation**: See `README.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **Hugo Docs**: https://gohugo.io/documentation/
- **Makefile Targets**: Run `make help`

## Quick Reference

| Command | Description |
|---------|-------------|
| `make build` | Build the site |
| `make serve` | Start dev server |
| `make docker-run` | Run in Docker |
| `make docker-stop` | Stop Docker |
| `make clean` | Clean generated files |
| `make help` | Show all targets |

---

**Time to First View**: < 2 minutes with Docker  
**Port**: 9003  
**Documentation Pages**: 19  
**Diagrams**: 110 SVGs
