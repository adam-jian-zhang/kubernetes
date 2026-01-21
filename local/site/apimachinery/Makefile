.PHONY: help convert build serve clean docker-build docker-run docker-stop docker-clean all

# Variables
DOCKER_IMAGE_NAME = k8s-apimachinery-docs
DOCKER_TAG = latest
DOCKER_PORT = 9001
HUGO_PORT = 9001

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

convert: ## Convert Mermaid diagrams to SVG
	@echo "Converting Mermaid diagrams to SVG..."
	@python3 scripts/convert_mermaid_to_svg.py

build: convert ## Build Hugo site (with Mermaid conversion)
	@echo "Building Hugo site..."
	@hugo --minify
	@echo "✓ Site built successfully in public/"

serve: ## Start Hugo development server
	@echo "Starting Hugo development server on http://localhost:$(HUGO_PORT)"
	@hugo server --port $(HUGO_PORT) --bind 0.0.0.0 --disableFastRender

clean: ## Clean generated files
	@echo "Cleaning generated files..."
	@rm -rf public resources .hugo_build.lock
	@find content -name "*.svg" -type f -delete 2>/dev/null || true
	@find static/diagrams -name "*.svg" -type f -delete 2>/dev/null || true
	@echo "✓ Cleaned"

docker-build: build ## Build Docker image
	@echo "Building Docker image: $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)"
	@docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) .
	@echo "✓ Docker image built successfully"
	@docker images | grep $(DOCKER_IMAGE_NAME)

docker-run: ## Run Docker container
	@echo "Starting Docker container on port $(DOCKER_PORT)..."
	@docker run -d --name $(DOCKER_IMAGE_NAME) -p $(DOCKER_PORT):$(DOCKER_PORT) $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
	@echo "✓ Container started: http://localhost:$(DOCKER_PORT)"
	@docker ps | grep $(DOCKER_IMAGE_NAME)

docker-stop: ## Stop Docker container
	@echo "Stopping Docker container..."
	@docker stop $(DOCKER_IMAGE_NAME) 2>/dev/null || true
	@docker rm $(DOCKER_IMAGE_NAME) 2>/dev/null || true
	@echo "✓ Container stopped"

docker-clean: docker-stop ## Remove Docker image and container
	@echo "Removing Docker image..."
	@docker rmi $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) 2>/dev/null || true
	@echo "✓ Docker image removed"

docker-logs: ## Show Docker container logs
	@docker logs -f $(DOCKER_IMAGE_NAME)

docker-shell: ## Open shell in running container
	@docker exec -it $(DOCKER_IMAGE_NAME) /bin/sh

all: clean build ## Clean and build everything

# Development workflow
dev: serve ## Alias for serve (development mode)

# Production workflow
prod: docker-build docker-run ## Build and run Docker container

# Quick rebuild
rebuild: clean build ## Clean and rebuild site

# Docker rebuild
docker-rebuild: docker-clean docker-build docker-run ## Clean, rebuild and run Docker container

