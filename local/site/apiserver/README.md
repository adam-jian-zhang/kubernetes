# k8s.io/apiserver Documentation Site

Static documentation site for the Kubernetes API server library, built with Hugo.

## Features

✨ **Modern UI**
- Clean, responsive design
- Light/dark mode toggle
- Smooth transitions and animations

📱 **Interactive Navigation**
- Collapsible sidebar menu
- Icon-only mode with tooltips
- Adjustable sidebar width (drag to resize)
- Active page highlighting

🎨 **Rich Content**
- 110 Mermaid diagrams converted to SVG
- Syntax-highlighted code blocks
- Responsive tables and images
- Previous/Next page navigation

🚀 **Performance**
- SVG diagrams for fast loading
- Minified assets
- Optimized images
- Static site generation

## Quick Start

### Prerequisites

- **Hugo** (v0.121.0 or later): https://gohugo.io/installation/
- **Python 3**: For processing scripts and serving
- **mermaid-cli** (optional): For SVG generation
  ```bash
  npm install -g @mermaid-js/mermaid-cli
  ```

### Build and Serve

```bash
# Process documentation and build site
make build

# Serve locally with Hugo (development)
make serve

# Or use Docker
make docker-run
```

The site will be available at http://localhost:9003

## Project Structure

```
apiserver/
├── hugo.toml                 # Hugo configuration
├── process_docs.py           # Documentation processor
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
├── Makefile                  # Build automation
├── content/                  # Generated Hugo content
├── static/                   # Static assets
│   └── diagrams/            # Generated SVG diagrams
├── themes/                   # Custom theme
│   └── apiserver-theme/
│       ├── layouts/         # HTML templates
│       └── static/          # Theme assets
│           ├── css/         # Stylesheets
│           └── js/          # JavaScript
└── public/                   # Generated site (after build)
```

## Development Workflow

### 1. Process Documentation

The `process_docs.py` script:
- Extracts Mermaid diagrams from markdown
- Converts diagrams to SVG (with content-based hashing)
- Replaces Mermaid code blocks with SVG images
- Adds Hugo front matter

```bash
python3 process_docs.py
```

### 2. Build Site

```bash
# Build with Hugo
hugo --minify

# Or use Makefile
make build
```

### 3. Local Development

```bash
# Start Hugo dev server with live reload
make serve

# Or manually
hugo server --port 9003
```

### 4. Docker Deployment

```bash
# Build and run with Docker
make docker-run

# Or use Docker Compose
docker-compose up -d

# View logs
make docker-logs

# Stop container
make docker-stop
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make help` | Show available targets |
| `make install` | Check dependencies |
| `make process` | Process markdown files |
| `make build` | Build Hugo site |
| `make serve` | Start development server |
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |
| `make docker-stop` | Stop Docker container |
| `make docker-logs` | View container logs |
| `make clean` | Remove generated files |
| `make rebuild` | Clean and rebuild |
| `make dev` | Start development environment |

## Theme Features

### Light/Dark Mode

Toggle between light and dark themes:
- Click the moon/sun icon in the sidebar header
- Preference is saved in localStorage
- Automatic theme persistence across sessions

### Collapsible Menu

Expand/collapse the sidebar:
- Click the hamburger menu icon
- Collapsed mode shows icons with tooltips
- State is saved in localStorage

### Adjustable Width

Resize the sidebar:
- Drag the vertical divider between sidebar and content
- Width is constrained between 200px and 600px
- Width preference is saved in localStorage

### Keyboard Navigation

- Arrow keys: Navigate between pages
- `/`: Focus search (if implemented)
- `Esc`: Close modals/overlays

## Customization

### Theme Colors

Edit `themes/apiserver-theme/static/css/style.css`:

```css
:root {
    --sidebar-bg: #2c3e50;
    --sidebar-active: #3498db;
    --text-link: #0066cc;
    /* ... more variables */
}
```

### Layout

Edit templates in `themes/apiserver-theme/layouts/`:
- `_default/baseof.html` - Base template
- `_default/single.html` - Single page template
- `_default/list.html` - List page template
- `partials/menu.html` - Navigation menu

### JavaScript

Modify behavior in `themes/apiserver-theme/static/js/`:
- `theme.js` - Theme toggling
- `menu.js` - Menu collapse/expand
- `resize.js` - Sidebar resizing

## Docker Deployment

### Build Image

```bash
docker build -t apiserver-docs:latest .
```

### Run Container

```bash
docker run -d \
  --name apiserver-docs \
  -p 9003:9003 \
  apiserver-docs:latest
```

### Docker Compose

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

### Health Check

The container includes a health check:
```bash
curl http://localhost:9003
```

## Production Deployment

### Static Hosting

The `public/` directory contains the complete static site:

```bash
# Build for production
make build

# Deploy public/ to:
# - GitHub Pages
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - Any static hosting service
```

### Server Deployment

```bash
# Using Docker
make docker-run

# Using nginx
cp -r public/* /var/www/html/

# Using Apache
cp -r public/* /var/www/html/
```

## Troubleshooting

### Mermaid Diagrams Not Rendering

If mermaid-cli is not installed, fallback SVGs are generated with the diagram code embedded. To get proper SVG diagrams:

```bash
npm install -g @mermaid-js/mermaid-cli
make clean
make build
```

### Port Already in Use

Change the port in `hugo.toml` or use a different port:

```bash
hugo server --port 8080
```

### Docker Build Fails

Ensure the site is built before creating the Docker image:

```bash
make build
docker build -t apiserver-docs .
```

## Performance Optimization

### SVG Optimization

SVGs are generated with transparent backgrounds and optimized for web:

```bash
# If you have svgo installed
find static/diagrams -name "*.svg" -exec svgo {} \;
```

### Asset Minification

Hugo automatically minifies assets when building with `--minify`:

```bash
hugo --minify
```

### Caching

Set appropriate cache headers in your web server:

```nginx
# nginx example
location ~* \.(svg|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Contributing

To update the documentation:

1. Edit markdown files in `../../docs/apiserver/`
2. Run `make process` to regenerate content
3. Run `make build` to rebuild the site
4. Test locally with `make serve`
5. Deploy the `public/` directory

## License

This documentation site is part of the Kubernetes project and follows the same Apache 2.0 license.

## Support

For issues or questions:
- Documentation: See the content in `../../docs/apiserver/`
- Hugo: https://gohugo.io/documentation/
- Kubernetes: https://kubernetes.io/docs/

---

**Generated**: January 2026  
**Hugo Version**: 0.121.0+  
**Python Version**: 3.11+  
**Port**: 9003
