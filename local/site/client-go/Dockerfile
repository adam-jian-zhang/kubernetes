# Simple Dockerfile to serve pre-built site
# Build the site locally first with: make build

FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy pre-built site
COPY public/ .

# Expose port
EXPOSE 9002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9002')" || exit 1

# Serve the site
CMD ["python3", "-m", "http.server", "9002"]
