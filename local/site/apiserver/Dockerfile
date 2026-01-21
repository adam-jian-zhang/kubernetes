FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the public directory
COPY public /app/public

# Expose port 9003
EXPOSE 9003

# Set working directory to public
WORKDIR /app/public

# Run Python HTTP server
CMD ["python3", "-m", "http.server", "9003"]
