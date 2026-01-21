#!/bin/bash
# Quick serve script for testing the site locally

PORT=9002

echo "======================================"
echo "Starting client-go Documentation Site"
echo "======================================"
echo

# Check if public directory exists
if [ ! -d "public" ]; then
    echo "Error: public/ directory not found"
    echo "Run './build.sh' first to build the site"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Warning: Port $PORT is already in use"
    echo
    read -p "Kill the process using port $PORT? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -ti:$PORT)
        kill -9 $PID
        echo "Killed process $PID"
        sleep 1
    else
        echo "Exiting..."
        exit 1
    fi
fi

echo "Starting HTTP server on port $PORT..."
echo
echo "  Local:   http://localhost:$PORT"
echo "  Network: http://$(ipconfig getifaddr en0 2>/dev/null || echo "N/A"):$PORT"
echo
echo "Press Ctrl+C to stop the server"
echo
echo "======================================"
echo

cd public && python3 -m http.server $PORT
