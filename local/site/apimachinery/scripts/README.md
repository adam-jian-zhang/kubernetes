# Helper Scripts

This directory contains helper scripts for building and managing the documentation site.

## Scripts

### convert_mermaid_to_svg.py

Converts Mermaid diagrams in markdown files to SVG images.

**What it does:**
1. Scans markdown files in `../content/` directory
2. Extracts mermaid code blocks
3. Converts them to SVG using `mmdc` (mermaid-cli)
4. Replaces mermaid blocks with SVG image links
5. Uses content hash as SVG filename for caching
6. Removes duplicate H1 titles from markdown files

**Usage:**
```bash
python3 scripts/convert_mermaid_to_svg.py
```

**Requirements:**
- Python 3.x
- `mmdc` (Mermaid CLI) - Install with: `npm install -g @mermaid-js/mermaid-cli`

### build-and-run.sh

Helper script to build and run the Docker container.

**What it does:**
1. Converts Mermaid diagrams to SVG
2. Builds the Hugo site
3. Builds the Docker image
4. Stops any existing container
5. Runs the new container on port 9001

**Usage:**
```bash
./scripts/build-and-run.sh
```

**Note:** This script is now superseded by the Makefile targets. Use `make prod` instead.

## Using the Makefile

The Makefile in the parent directory provides convenient targets for all common operations. See `make help` for available targets.

**Common workflows:**

```bash
# Development
make serve              # Start Hugo dev server

# Build
make build              # Build Hugo site with Mermaid conversion
make convert            # Convert Mermaid diagrams only

# Docker
make docker-build       # Build Docker image
make docker-run         # Run Docker container
make docker-stop        # Stop Docker container
make prod               # Build and run Docker container

# Maintenance
make clean              # Clean generated files
make rebuild            # Clean and rebuild
make docker-rebuild     # Clean, rebuild and run Docker
```

