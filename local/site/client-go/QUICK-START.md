# Quick Start Guide

## 🚀 Get Started in 30 Seconds

### Option 1: Makefile (Recommended)

```bash
# Navigate to site directory
cd local/site/client-go

# Build and serve
make build
make serve

# Visit http://localhost:9002
```

### Option 2: Scripts

```bash
# Build everything
./build.sh

# Serve locally
./serve.sh

# Visit http://localhost:9002
```

### Option 3: Docker

```bash
# Build and run
make docker-run

# Visit http://localhost:9002
```

## 📋 Common Tasks

### Development

```bash
# Start dev server with live reload
make dev
# Visit http://localhost:1313
```

### Building

```bash
# Full build
make build

# Clean and rebuild
make rebuild

# Update from docs
make update
```

### Testing

```bash
# Run tests
make test

# Check status
make status

# Show info
make info
```

### Docker

```bash
# Build image
make docker-build

# Run container
make docker-run

# View logs
make docker-logs

# Stop container
make docker-stop
```

### Docker Compose

```bash
# Start services
make docker-compose-up

# View logs
make docker-compose-logs

# Stop services
make docker-compose-down
```

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Check what's using port 9002
lsof -i :9002

# Or let the serve script handle it
./serve.sh
```

### Build Fails

```bash
# Clean and rebuild
make clean
make build
```

### Docker Issues

```bash
# Clean Docker resources
make docker-clean

# Rebuild from scratch
make docker-build
```

## 📚 Documentation

- **Full README**: `README.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Site Summary**: `SITE-SUMMARY.md`
- **All Commands**: `make help`

## 🎯 Key Features

- ✅ Light/Dark mode toggle
- ✅ Collapsible sidebar
- ✅ Resizable sidebar (drag divider)
- ✅ Mobile responsive
- ✅ Mermaid diagrams
- ✅ Code copy buttons
- ✅ Smooth scrolling

## 🌐 URLs

After starting the server, visit:

- Home: http://localhost:9002
- Overview: http://localhost:9002/00-overview/
- Core Packages: http://localhost:9002/01-core-packages/
- Configuration: http://localhost:9002/02-configuration/
- Controllers: http://localhost:9002/03-controller-infrastructure/
- Advanced: http://localhost:9002/04-advanced-features/
- Utilities: http://localhost:9002/05-utilities/
- Examples: http://localhost:9002/06-examples/
- Index: http://localhost:9002/index-page/

## 💡 Tips

1. **Use Makefile**: It handles all dependencies and provides helpful output
2. **Dev Mode**: Use `make dev` for development with live reload
3. **Docker**: Use Docker for production-like testing
4. **Clean Build**: Run `make clean` before rebuilding if you encounter issues
5. **Check Status**: Run `make status` to see what's built and running

## 🆘 Need Help?

```bash
# Show all commands
make help

# Show detailed info
make info

# Check dependencies
make install

# Validate configuration
make validate
```

## 📦 What Gets Built

```
public/
├── index.html              # Home page
├── 00-overview/            # Overview
├── 01-core-packages/       # Core packages
├── 02-configuration/       # Configuration
├── 03-controller-infrastructure/  # Controllers
├── 04-advanced-features/   # Advanced features
├── 05-utilities/           # Utilities
├── 06-examples/            # Examples
├── index-page/             # Index
├── css/                    # Styles
├── js/                     # JavaScript
└── images/                 # Images
```

## 🔄 Update Workflow

When documentation changes:

```bash
# 1. Update markdown files in ../../docs/client-go/

# 2. Rebuild site
make update

# 3. Test locally
make serve

# 4. Deploy
make docker-run
# OR
# Upload public/ to hosting service
```

## ⚡ Performance

- **Build Time**: ~240ms
- **Site Size**: ~400KB
- **Pages**: 15 HTML pages
- **Load Time**: Fast (static HTML)

## 🎨 Customization

### Change Port

Edit `Makefile`:
```makefile
PORT := 9002  # Change to your preferred port
```

### Change Theme Colors

Edit `themes/client-go-docs/static/css/style.css`:
```css
:root[data-theme="light"] {
    --bg-primary: #ffffff;
    /* ... other colors ... */
}
```

### Add Pages

1. Add markdown file to `../../docs/client-go/`
2. Update `process_content.py` file mapping
3. Update `hugo.toml` menu
4. Run `make rebuild`

---

**Ready to go!** Start with `make build && make serve`
