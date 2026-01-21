FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the public folder
COPY public /app/public

# Expose port 9001
EXPOSE 9001

# Change to public directory and start HTTP server
WORKDIR /app/public
CMD ["python3", "-m", "http.server", "9001"]

