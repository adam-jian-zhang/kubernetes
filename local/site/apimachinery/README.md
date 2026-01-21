# k8s.io/apimachinery Documentation Site

This is a static documentation site for the `k8s.io/apimachinery` library, built with Hugo.

## Features

- 📚 **Comprehensive Documentation**: Detailed coverage of all apimachinery packages
- 🎨 **Modern UI**: Clean, responsive design with light/dark mode
- 📊 **Interactive Diagrams**: Mermaid diagrams converted to SVG for fast loading
- 🔍 **Easy Navigation**: Collapsible sidebar with adjustable width
- 🐳 **Docker Ready**: Packaged for easy deployment

## Quick Start

### Using Make (Recommended)

```bash
# Show all available targets
make help

# Development - Start Hugo dev server
make serve

# Build the site
make build

# Build and run Docker container
make prod
```

### Manual Commands

```bash
# Convert Mermaid diagrams
python3 scripts/convert_mermaid_to_svg.py

# Build Hugo site
hugo --minify

# Build Docker image
docker build -t k8s-apimachinery-docs:latest .

# Run Docker container
docker run -d --name k8s-apimachinery-docs -p 9001:9001 k8s-apimachinery-docs:latest
```

## Project Structure

```
.
├── Makefile                    # Build automation
├── Dockerfile                  # Docker image definition
├── hugo.toml                   # Hugo configuration
├── content/                    # Markdown content (generated)
│   ├── _index.md              # Home page
│   ├── 00-overview.md         # Architecture overview
│   ├── 01-runtime-package.md  # Runtime package docs
│   └── ...                    # More package docs
├── static/
│   └── diagrams/              # Generated SVG diagrams
├── themes/
│   └── apimachinery-theme/    # Custom Hugo theme
│       ├── layouts/           # HTML templates
│       ├── static/
│       │   ├── css/          # Stylesheets
│       │   └── js/           # JavaScript
│       └── theme.toml        # Theme metadata
├── scripts/                   # Helper scripts
│   ├── convert_mermaid_to_svg.py  # Mermaid → SVG converter
│   ├── build-and-run.sh      # Build and run script
│   └── README.md             # Scripts documentation
└── public/                    # Generated site (created by Hugo)
```

## Makefile Targets

### Development

- `make serve` - Start Hugo development server on http://localhost:9001
- `make dev` - Alias for `serve`

### Building

- `make convert` - Convert Mermaid diagrams to SVG
- `make build` - Build Hugo site (includes Mermaid conversion)
- `make clean` - Clean generated files
- `make rebuild` - Clean and rebuild site
- `make all` - Clean and build everything

### Docker

- `make docker-build` - Build Docker image
- `make docker-run` - Run Docker container
- `make docker-stop` - Stop Docker container
- `make docker-clean` - Remove Docker image and container
- `make docker-logs` - Show container logs
- `make docker-shell` - Open shell in running container
- `make docker-rebuild` - Clean, rebuild and run Docker
- `make prod` - Build and run Docker container (production workflow)

## Requirements

### For Development

- **Hugo** (v0.153.2 or later with extended support)
  ```bash
  # macOS
  brew install hugo
  
  # Linux
  snap install hugo
  
  # Windows
  choco install hugo-extended
  ```

- **Python 3.x** (for Mermaid conversion)
  ```bash
  python3 --version
  ```

- **Mermaid CLI** (for diagram conversion)
  ```bash
  npm install -g @mermaid-js/mermaid-cli
  ```

### For Docker Deployment

- **Docker** (for building and running the container)
  ```bash
  docker --version
  ```

## Features in Detail

### Light/Dark Mode

Toggle between light and dark themes using the button in the left sidebar. The preference is saved in browser localStorage.

### Collapsible Sidebar

Click the hamburger menu (☰) in the sidebar to collapse/expand the navigation. When collapsed, the sidebar shows only icons with tooltips.

### Resizable Sidebar

Drag the vertical divider between the sidebar and content to adjust widths. The position is saved in localStorage.

### Mermaid Diagrams

Mermaid diagrams in the source markdown are automatically converted to SVG during the build process. SVG filenames use content hashes for efficient caching.

## Deployment

### Using Docker

The recommended deployment method is using Docker:

```bash
# Build and run
make prod

# Or manually
make docker-build
make docker-run

# Access the site
open http://localhost:9001
```

### Using the Docker Image

```bash
# Build
docker build -t k8s-apimachinery-docs:latest .

# Run
docker run -d \
  --name k8s-apimachinery-docs \
  -p 9001:9001 \
  k8s-apimachinery-docs:latest

# Stop
docker stop k8s-apimachinery-docs
docker rm k8s-apimachinery-docs

# View logs
docker logs -f k8s-apimachinery-docs
```

### Static File Hosting

You can also deploy the `public/` directory to any static file hosting service:

- **GitHub Pages**: Push `public/` to `gh-pages` branch
- **Netlify**: Connect repository and set build command to `hugo --minify`
- **Vercel**: Import repository and set framework to Hugo
- **AWS S3**: Sync `public/` to S3 bucket with static website hosting
- **Nginx**: Copy `public/` to nginx web root

## Development Workflow

1. **Start development server**
   ```bash
   make serve
   ```

2. **Edit content** in `content/` directory

3. **View changes** at http://localhost:9001 (auto-reload enabled)

4. **Build for production**
   ```bash
   make build
   ```

5. **Test Docker image**
   ```bash
   make prod
   ```

## Customization

### Theme

The custom theme is located in `themes/apimachinery-theme/`. Key files:

- `layouts/_default/baseof.html` - Base template
- `layouts/_default/single.html` - Single page template
- `layouts/_default/list.html` - List page template
- `static/css/style.css` - Main stylesheet
- `static/js/theme.js` - Theme toggle logic
- `static/js/menu.js` - Menu collapse logic
- `static/js/resize.js` - Sidebar resize logic

### Colors

Edit CSS variables in `themes/apimachinery-theme/static/css/style.css`:

```css
:root {
    --primary-color: #326ce5;
    --text-color: #333;
    --bg-color: #fff;
    /* ... more variables ... */
}

[data-theme="dark"] {
    --text-color: #e0e0e0;
    --bg-color: #1a1a1a;
    /* ... dark theme overrides ... */
}
```

## Troubleshooting

### Hugo build fails

- Ensure Hugo extended version is installed: `hugo version`
- Check for syntax errors in markdown files
- Verify front matter is valid YAML

### Mermaid diagrams not converting

- Install Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`
- Test mmdc: `mmdc --version`
- Check for syntax errors in Mermaid code

### Docker build fails

- Ensure Docker is running: `docker ps`
- Check disk space: `docker system df`
- Clean Docker cache: `docker system prune`

### Port 9001 already in use

- Stop existing server: `make docker-stop`
- Or use a different port: Edit `DOCKER_PORT` in Makefile

## Contributing

This documentation is generated from the source code in `staging/src/k8s.io/apimachinery` of the Kubernetes repository.

To update the documentation:

1. Modify markdown files in `../../docs/apimachinery/`
2. Run `make build` to regenerate the site
3. Test changes with `make serve`
4. Build Docker image with `make docker-build`

## License

Apache License 2.0

## Additional Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Mermaid Documentation](https://mermaid.js.org/)
- [Kubernetes API Conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md)
- [k8s.io/apimachinery Source](https://github.com/kubernetes/kubernetes/tree/master/staging/src/k8s.io/apimachinery)
