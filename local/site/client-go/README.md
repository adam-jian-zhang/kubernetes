# client-go Documentation Site

Static documentation site for k8s.io/client-go built with Hugo.

## Features

- ✅ Light/Dark mode toggle
- ✅ Collapsible sidebar menu
- ✅ Adjustable sidebar width (drag to resize)
- ✅ Responsive design for mobile
- ✅ Mermaid diagrams converted to SVG for fast loading
- ✅ Syntax highlighting for code blocks
- ✅ Copy code button for code blocks
- ✅ Auto-generated table of contents
- ✅ Smooth scrolling

## Prerequisites

### For Docker (Recommended)
- Docker
- Docker Compose (optional, but recommended)

That's it! Docker handles everything else (Hugo, Python, mermaid-cli).

### For Local Build
- Hugo (v0.100.0+)
- Python 3.x (for serving)
- mermaid-cli (for converting diagrams to SVG)
  ```bash
  npm install -g @mermaid-js/mermaid-cli
  ```

## Building the Site

### 🚀 Quick Start with Docker (Recommended)

The easiest way to build and run the site is with Docker:

```bash
# One command to build and run everything!
make quick-docker

# Visit http://localhost:9002
```

This will:
- Build the Docker image with Hugo and mermaid-cli
- Process markdown content and convert diagrams to SVG
- Build the site with Hugo
- Serve on port 9002

**📖 See [DOCKER-SETUP.md](DOCKER-SETUP.md) for detailed Docker documentation.**

### Alternative: Local Build

If you prefer to build locally:

```bash
# Build the site
make build

# Serve locally
make serve

# Or use Hugo dev server with live reload
make dev

# Show all available commands
make help
```

### Manual Build

#### 1. Process Content and Convert Diagrams

Convert markdown files from the docs directory to Hugo content and convert Mermaid diagrams to SVG:

```bash
python3 process_mermaid.py
```

This script will:
- Copy markdown files from `../docs/client-go/` to `content/`
- Fix internal links (convert `.md` to `/` for Hugo)
- Extract Mermaid diagrams from markdown
- Generate SVG files with hash-based names (e.g., `diagram_8ff26eefb814d476.svg`)
- Replace Mermaid code blocks with SVG image references
- Add Hugo front matter with weights for ordering

#### 2. Build with Hugo

```bash
hugo --minify
```

The site will be built to the `public/` directory.

#### 3. Serve Locally

```bash
# Using Hugo's built-in server (for development)
hugo server -D

# Or using Python HTTP server (production-like)
cd public && python3 -m http.server 9002
```

Visit http://localhost:9002

## Makefile Commands

The project includes a comprehensive Makefile for easy management:

### Common Commands

```bash
make help          # Show all available commands
make build         # Build the complete site
make serve         # Serve locally on port 9002
make dev           # Start Hugo dev server with live reload
make clean         # Remove generated files
make test          # Run basic tests
make status        # Show current status
make info          # Show detailed information
```

### Docker Commands

```bash
make docker-build  # Build Docker image
make docker-run    # Build and run in Docker
make docker-stop   # Stop and remove container
make docker-logs   # Show container logs
make docker-clean  # Remove image and container
```

### Docker Compose Commands

```bash
make docker-compose-up       # Start with Docker Compose
make docker-compose-down     # Stop services
make docker-compose-logs     # Show logs
make docker-compose-rebuild  # Rebuild and restart
```

### Utility Commands

```bash
make install       # Check dependencies
make validate      # Validate Hugo config
make lint          # Check for issues
make size          # Show site size
make urls          # List all URLs
make version       # Show tool versions
make all           # Build everything
make rebuild       # Clean and rebuild
make update        # Update from docs and rebuild
```

## Docker Deployment

### Build Docker Image

```bash
# Build the site first
hugo --minify

# Build Docker image
docker build -t client-go-docs:latest .
```

### Run Container

```bash
docker run -d -p 9002:9002 --name client-go-docs client-go-docs:latest
```

Visit http://localhost:9002

### Stop Container

```bash
docker stop client-go-docs
docker rm client-go-docs
```

## Project Structure

```
.
├── archetypes/          # Hugo archetypes
├── content/             # Processed markdown content (generated)
├── public/              # Built site (generated)
├── static/              # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── themes/
│   └── client-go-docs/  # Custom theme
│       ├── layouts/
│       │   ├── _default/
│       │   └── partials/
│       └── static/
├── hugo.toml            # Hugo configuration
├── process_content.py   # Content processing script
├── Dockerfile           # Docker configuration
└── README.md            # This file
```

## Theme Features

### Light/Dark Mode

Click the moon/sun icon in the sidebar header to toggle between light and dark themes. The preference is saved in localStorage.

### Collapsible Sidebar

- **Desktop**: Click the menu icon in the content header to collapse/expand the sidebar
- **Mobile**: Click the menu icon to show/hide the sidebar overlay

### Resizable Sidebar

On desktop, drag the vertical divider between the sidebar and content to adjust the sidebar width. The width is saved in localStorage.

### Mermaid Diagrams

Mermaid diagrams are rendered in the browser using mermaid.js. They automatically update when switching between light and dark modes.

## Customization

### Colors

Edit `themes/client-go-docs/static/css/style.css` and modify the CSS variables in the `:root` selectors for light and dark themes.

### Navigation

Edit `hugo.toml` and modify the `[[menu.main]]` sections to add, remove, or reorder navigation items.

### Layout

Edit the layout files in `themes/client-go-docs/layouts/` to customize the HTML structure.

## Updating Content

1. Update markdown files in `../../docs/client-go/`
2. Run `python3 process_content.py` to regenerate content
3. Run `hugo --minify` to rebuild the site
4. Rebuild Docker image if deploying via Docker

## Troubleshooting

### Hugo not found

Install Hugo from https://gohugo.io/installation/

### Port 9002 already in use

Change the port in:
- `hugo.toml` (baseURL)
- `Dockerfile` (EXPOSE and CMD)
- Run command

### Mermaid diagrams not rendering

Ensure you have an internet connection as mermaid.js is loaded from CDN. For offline use, download mermaid.js and serve it locally.

## License

Apache License 2.0 - See LICENSE file for details.
