.PHONY: help install process build serve docker-build docker-run docker-stop clean

HUGO_VERSION := 0.121.0
PYTHON := python3
DOCKER_IMAGE := apiserver-docs
DOCKER_TAG := latest
PORT := 9003

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies (Hugo, mermaid-cli)
	@echo "Installing dependencies..."
	@command -v hugo >/dev/null 2>&1 || { \
		echo "Hugo not found. Please install Hugo $(HUGO_VERSION) from https://gohugo.io/installation/"; \
		exit 1; \
	}
	@echo "✓ Hugo is installed"
	@command -v mmdc >/dev/null 2>&1 || { \
		echo "⚠ mermaid-cli (mmdc) not found. SVG generation will use fallback."; \
		echo "  Install with: npm install -g @mermaid-js/mermaid-cli"; \
	}
	@echo "✓ Dependencies checked"

process: ## Process markdown files and extract Mermaid diagrams
	@echo "Processing documentation files..."
	@$(PYTHON) process_docs.py
	@echo "✓ Documentation processed"

build: process ## Build Hugo site
	@echo "Building Hugo site..."
	@hugo --minify
	@echo "✓ Site built to public/"

serve: process ## Serve site locally with Hugo
	@echo "Starting Hugo development server on http://localhost:$(PORT)..."
	@hugo server --port $(PORT) --bind 0.0.0.0

docker-build: build ## Build Docker image
	@echo "Building Docker image $(DOCKER_IMAGE):$(DOCKER_TAG)..."
	@docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "✓ Docker image built"

docker-run: docker-build ## Run Docker container
	@echo "Starting Docker container on port $(PORT)..."
	@docker run -d --name apiserver-docs -p $(PORT):$(PORT) $(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "✓ Container running at http://localhost:$(PORT)"
	@echo "  Stop with: make docker-stop"

docker-stop: ## Stop and remove Docker container
	@echo "Stopping Docker container..."
	@docker stop apiserver-docs 2>/dev/null || true
	@docker rm apiserver-docs 2>/dev/null || true
	@echo "✓ Container stopped"

docker-logs: ## Show Docker container logs
	@docker logs -f apiserver-docs

clean: ## Clean generated files
	@echo "Cleaning generated files..."
	@rm -rf public/ content/ static/diagrams/ temp_mermaid/
	@echo "✓ Cleaned"

rebuild: clean build ## Clean and rebuild

dev: ## Start development environment
	@echo "Starting development environment..."
	@$(MAKE) process
	@$(MAKE) serve

# Quick commands
.PHONY: dev rebuild
