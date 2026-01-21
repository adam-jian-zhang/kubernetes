#!/bin/bash

set -e

echo "=== Building Apimachinery Documentation Site ==="

# Convert documentation and mermaid diagrams to SVG
echo "Converting documentation and mermaid diagrams..."
python3 convert_mermaid_to_svg.py

# Build Hugo site
echo "Building Hugo site..."
hugo --minify

# Build Docker image
echo "Building Docker image..."
docker build -t apimachinery-docs:latest .

# Stop and remove existing container if running
if docker ps -a | grep -q apimachinery-docs; then
    echo "Stopping existing container..."
    docker stop apimachinery-docs || true
    docker rm apimachinery-docs || true
fi

# Run container
echo "Starting container..."
docker run -d -p 9001:9001 --name apimachinery-docs apimachinery-docs:latest

echo ""
echo "=== Site is running ==="
echo "URL: http://localhost:9001"
echo ""
echo "Features:"
echo "  ✓ 26 Mermaid diagrams converted to SVG"
echo "  ✓ Light/Dark mode toggle (🌙/☀️)"
echo "  ✓ Collapsible sidebar menu"
echo "  ✓ Resizable sidebar (drag divider)"
echo "  ✓ Responsive design"
echo ""
echo "Commands:"
echo "  Stop:   docker stop apimachinery-docs"
echo "  Logs:   docker logs apimachinery-docs"
echo "  Remove: docker rm apimachinery-docs"
