#!/bin/bash
set -e

echo "======================================"
echo "Building client-go Documentation Site"
echo "======================================"
echo

# Step 1: Process content
echo "Step 1: Processing markdown content..."
python3 process_content.py
echo "✓ Content processed"
echo

# Step 2: Build with Hugo
echo "Step 2: Building site with Hugo..."
hugo --minify
echo "✓ Site built to public/"
echo

# Step 3: Build Docker image (optional)
if [ "$1" == "--docker" ]; then
    echo "Step 3: Building Docker image..."
    docker build -t client-go-docs:latest .
    echo "✓ Docker image built"
    echo
    
    echo "To run the container:"
    echo "  docker run -d -p 9002:9002 --name client-go-docs client-go-docs:latest"
    echo
    echo "To stop the container:"
    echo "  docker stop client-go-docs && docker rm client-go-docs"
else
    echo "To serve locally:"
    echo "  cd public && python3 -m http.server 9002"
    echo
    echo "Or build Docker image:"
    echo "  ./build.sh --docker"
fi

echo
echo "======================================"
echo "Build complete!"
echo "======================================"
