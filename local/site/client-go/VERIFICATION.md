# Site Verification Guide

This document provides commands to verify that the client-go documentation site was built correctly with all SVG diagrams.

## ✅ Quick Verification

Run these commands to verify the site:

```bash
cd /Users/adamz/work/k8s/kubernetes/local/site/client-go

# Check if public directory exists
ls -la public/

# Count HTML pages (should be 9+)
find public -name "index.html" | wc -l

# Count SVG files (should be 23)
ls public/images/*.svg | wc -l

# Check SVG references in HTML (should be 23)
find public -name "*.html" -exec grep -o "mermaid-diagram" {} \; | wc -l
```

## 📊 Detailed Verification

### 1. Check Site Structure

```bash
# View site structure
tree -L 2 public/

# Expected output:
# public/
# ├── 00-overview/
# ├── 01-core-packages/
# ├── 02-configuration/
# ├── 03-controller-infrastructure/
# ├── 04-advanced-features/
# ├── 05-utilities/
# ├── 06-examples/
# ├── index-page/
# ├── css/
# ├── js/
# ├── images/
# ├── index.html
# └── sitemap.xml
```

### 2. Verify SVG Files

```bash
# List all SVG files with sizes
ls -lh public/images/

# Expected: 23 SVG files, each 10-30 KB

# Verify SVG file count
ls public/images/*.svg | wc -l
# Expected: 23

# Check total SVG size
du -sh public/images/
# Expected: ~468K
```

### 3. Verify SVG References in HTML

```bash
# Find all unique SVG references
find public -name "*.html" -exec grep -o 'src="/images/diagram_[^"]*\.svg"' {} \; | sort -u

# Expected: 23 unique SVG references

# Count total SVG references
find public -name "*.html" -exec grep -o "mermaid-diagram" {} \; | wc -l
# Expected: 23

# List pages with diagrams
find public -name "*.html" -exec grep -l "mermaid-diagram" {} \;
# Expected: 7 pages
```

### 4. Verify Content Files

```bash
# List content files
ls -la content/

# Expected files:
# _index.md (README)
# 00-overview.md
# 01-core-packages.md
# 02-configuration.md
# 03-controller-infrastructure.md
# 04-advanced-features.md
# 05-utilities.md
# 06-examples.md
# index-page.md (INDEX)
```

### 5. Verify Assets

```bash
# Check CSS
ls -lh public/css/style.css
# Expected: ~15-20 KB

# Check JavaScript
ls -lh public/js/main.js
# Expected: ~2-3 KB

# Check total site size
du -sh public/
# Expected: ~1.5M
```

### 6. Verify HTML Content

```bash
# Check homepage has SVG
grep "mermaid-diagram" public/index.html
# Expected: Should find 1 diagram reference

# Check controller infrastructure page (most diagrams)
grep -o "mermaid-diagram" public/03-controller-infrastructure/index.html | wc -l
# Expected: 6 diagrams

# Verify no Mermaid.js script tags (we're using SVG, not client-side)
grep -r "mermaid.esm" public/
# Expected: No results (empty output)
```

### 7. Verify Theme Features

```bash
# Check for theme toggle
grep "data-theme" public/index.html
# Expected: Found in <html> tag

# Check for Font Awesome
grep "font-awesome" public/index.html
# Expected: Found in <link> tag

# Check for sidebar toggle
grep "toggle-sidebar" public/js/main.js
# Expected: Found in JavaScript
```

### 8. Verify Docker Files

```bash
# Check Dockerfile exists
cat Dockerfile

# Check .dockerignore exists
cat .dockerignore

# Check docker-compose.yml exists
cat docker-compose.yml
```

## 🔍 Content Verification

### Verify Each Page Has Correct Diagrams

```bash
# README (1 diagram)
grep -o "diagram_8ff26eefb814d476.svg" public/index.html
# Expected: Found

# Overview (3 diagrams)
grep -o "diagram_[^\"]*\.svg" public/00-overview/index.html | wc -l
# Expected: 3

# Core Packages (4 diagrams)
grep -o "diagram_[^\"]*\.svg" public/01-core-packages/index.html | wc -l
# Expected: 4

# Configuration (3 diagrams)
grep -o "diagram_[^\"]*\.svg" public/02-configuration/index.html | wc -l
# Expected: 3

# Controller Infrastructure (6 diagrams)
grep -o "diagram_[^\"]*\.svg" public/03-controller-infrastructure/index.html | wc -l
# Expected: 6

# Advanced Features (5 diagrams)
grep -o "diagram_[^\"]*\.svg" public/04-advanced-features/index.html | wc -l
# Expected: 5

# Utilities (1 diagram)
grep -o "diagram_[^\"]*\.svg" public/05-utilities/index.html | wc -l
# Expected: 1

# Examples (0 diagrams)
grep -o "diagram_[^\"]*\.svg" public/06-examples/index.html | wc -l
# Expected: 0
```

## 🧪 Functional Testing

### Test Local Serving

```bash
# Serve the site
make serve

# In another terminal, test the site
curl -s http://localhost:9002 | grep "<title>"
# Expected: <title>client-go Documentation</title>

# Test SVG file is accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost:9002/images/diagram_8ff26eefb814d476.svg
# Expected: 200

# Test CSS is accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost:9002/css/style.css
# Expected: 200

# Test JS is accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost:9002/js/main.js
# Expected: 200
```

### Test Docker Build

```bash
# Build Docker image
make docker-build

# Verify image exists
docker images | grep client-go-docs
# Expected: client-go-docs latest ...

# Run container
make docker-run

# Verify container is running
docker ps | grep client-go-docs
# Expected: client-go-docs container running

# Test site in container
curl -s http://localhost:9002 | grep "<title>"
# Expected: <title>client-go Documentation</title>

# Stop container
make docker-stop
```

## 📋 Checklist

Use this checklist to verify the site:

- [ ] Public directory exists
- [ ] 9+ HTML pages generated
- [ ] 23 SVG files in public/images/
- [ ] 23 SVG references in HTML
- [ ] CSS file exists (~15-20 KB)
- [ ] JavaScript file exists (~2-3 KB)
- [ ] No Mermaid.js script tags in HTML
- [ ] Theme toggle present in HTML
- [ ] Sidebar toggle present in JavaScript
- [ ] Dockerfile exists
- [ ] .dockerignore exists
- [ ] docker-compose.yml exists
- [ ] Makefile has 30+ targets
- [ ] README.md documentation exists
- [ ] Site serves correctly on port 9002
- [ ] Docker image builds successfully
- [ ] Docker container runs successfully

## 🎯 Expected Results Summary

| Metric | Expected | Command |
|--------|----------|---------|
| HTML pages | 9+ | `find public -name "index.html" \| wc -l` |
| SVG files | 23 | `ls public/images/*.svg \| wc -l` |
| SVG references | 23 | `find public -name "*.html" -exec grep -o "mermaid-diagram" {} \\; \| wc -l` |
| Pages with diagrams | 7 | `find public -name "*.html" -exec grep -l "mermaid-diagram" {} \\; \| wc -l` |
| Site size | ~1.5M | `du -sh public/` |
| SVG total size | ~468K | `du -sh public/images/` |
| CSS size | ~15-20K | `ls -lh public/css/style.css` |
| JS size | ~2-3K | `ls -lh public/js/main.js` |

## ✅ Success Criteria

The site is correctly built if:

1. ✅ All 23 SVG files are generated in `public/images/`
2. ✅ All 23 SVG files are referenced in HTML pages
3. ✅ No Mermaid.js client-side rendering code in HTML
4. ✅ Site structure matches expected layout
5. ✅ All assets (CSS, JS) are present
6. ✅ Docker files are present and functional
7. ✅ Site serves correctly on port 9002
8. ✅ All pages are accessible and render correctly

## 🔧 Troubleshooting

### Issue: SVG files missing

```bash
# Regenerate SVG files
python3 process_mermaid.py

# Rebuild site
hugo --minify
```

### Issue: SVG references not in HTML

```bash
# Check content files have SVG references
grep "mermaid-diagram" content/*.md

# If not, regenerate content
python3 process_mermaid.py
hugo --minify
```

### Issue: Site not serving

```bash
# Check if port is in use
lsof -i :9002

# Try different port
PORT=9003 make serve
```

### Issue: Docker build fails

```bash
# Check if public/ exists
ls -la public/

# Rebuild site first
make build

# Then build Docker
make docker-build
```

## 📞 Support

If verification fails:

1. Check the build logs for errors
2. Verify all prerequisites are installed (`make install`)
3. Clean and rebuild (`make rebuild`)
4. Check the README.md for detailed instructions
5. Review TROUBLESHOOTING section in DEPLOYMENT.md

---

**Last Updated**: January 15, 2026  
**Version**: 1.0.0
