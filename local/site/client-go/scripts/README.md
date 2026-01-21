# Build Scripts

This directory contains helper scripts for building the client-go documentation site.

## Scripts

### `process_mermaid.py`

Main content processing script that:
- Copies markdown files from `../docs/client-go/` to `content/`
- Fixes internal links (converts `.md` to `/` for Hugo)
- Extracts Mermaid diagrams from markdown
- Converts Mermaid to SVG using mermaid-cli
- Generates hash-based SVG filenames
- Replaces Mermaid code blocks with SVG image references
- Adds Hugo front matter with weights

**Usage:**
```bash
python3 scripts/process_mermaid.py
```

**Requirements:**
- Python 3.x
- mermaid-cli (mmdc)

### `process_content.py`

Legacy script (kept for reference). Use `process_mermaid.py` instead.

### `build.sh`

Shell script for building the site locally.

**Usage:**
```bash
./scripts/build.sh
```

### `serve.sh`

Shell script for serving the built site locally.

**Usage:**
```bash
./scripts/serve.sh
```

## Docker Build

When using Docker, these scripts are automatically executed inside the container during the build process. See the `Dockerfile` for details.

## Notes

- All scripts should be run from the project root directory
- The `process_mermaid.py` script requires mermaid-cli to be installed
- For Docker builds, all dependencies are handled automatically
