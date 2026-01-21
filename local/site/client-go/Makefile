.PHONY: help build serve clean docker docker-build docker-run docker-stop docker-clean content hugo dev install test lint validate all

# Variables
HUGO_VERSION := 0.154.5
DOCKER_IMAGE := client-go-docs
DOCKER_TAG := latest
DOCKER_CONTAINER := client-go-docs
PORT := 9002
HUGO_PORT := 1313

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

## help: Show this help message
help:
	@echo "$(BLUE)client-go Documentation Site - Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/## /  /' | column -t -s ':' | sed 's/^/  /'
	@echo ""
	@echo "$(YELLOW)Quick Start (Recommended):$(NC)"
	@echo "  make quick-docker        # 🚀 Build and run with Docker (easiest!)"
	@echo ""
	@echo "$(YELLOW)Other Examples:$(NC)"
	@echo "  make build               # Build the site locally"
	@echo "  make serve               # Serve locally on port $(PORT)"
	@echo "  make dev                 # Start Hugo dev server"
	@echo "  make docker-compose-up   # Start with Docker Compose"
	@echo "  make all                 # Build everything"
	@echo ""

## content: Process markdown content and convert Mermaid to SVG
content:
	@echo "$(BLUE)Processing markdown content and converting Mermaid to SVG...$(NC)"
	@python3 scripts/process_mermaid.py
	@echo "$(GREEN)✓ Content processed and diagrams converted$(NC)"

## hugo: Build site with Hugo
hugo: content
	@echo "$(BLUE)Building site with Hugo...$(NC)"
	@hugo --minify
	@echo "$(GREEN)✓ Site built to public/$(NC)"

## build: Build the complete site (content + hugo)
build: hugo
	@echo "$(GREEN)✓ Build complete!$(NC)"

## serve: Serve the built site locally on port $(PORT)
serve:
	@if [ ! -d "public" ]; then \
		echo "$(RED)Error: public/ directory not found$(NC)"; \
		echo "$(YELLOW)Run 'make build' first$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Starting HTTP server on port $(PORT)...$(NC)"
	@echo "$(GREEN)Visit: http://localhost:$(PORT)$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@cd public && python3 -m http.server $(PORT)

## dev: Start Hugo development server with live reload
dev:
	@echo "$(BLUE)Starting Hugo development server...$(NC)"
	@echo "$(GREEN)Visit: http://localhost:$(HUGO_PORT)$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@hugo server -D --port $(HUGO_PORT)

## clean: Remove generated files
clean:
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	@rm -rf public/
	@rm -rf content/
	@rm -rf resources/
	@echo "$(GREEN)✓ Clean complete$(NC)"

## docker-build: Build Docker image (includes site build)
docker-build:
	@echo "$(BLUE)Building Docker image (this will build the site inside Docker)...$(NC)"
	@docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"
	@echo "$(YELLOW)Note: Site was built inside Docker container$(NC)"

## docker-run: Run site in Docker container
docker-run: docker-build
	@echo "$(BLUE)Starting Docker container...$(NC)"
	@docker run -d \
		--name $(DOCKER_CONTAINER) \
		-p $(PORT):$(PORT) \
		--restart unless-stopped \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)✓ Container started: $(DOCKER_CONTAINER)$(NC)"
	@echo "$(GREEN)Visit: http://localhost:$(PORT)$(NC)"
	@echo ""
	@echo "$(YELLOW)Useful commands:$(NC)"
	@echo "  docker logs $(DOCKER_CONTAINER)       # View logs"
	@echo "  docker logs -f $(DOCKER_CONTAINER)    # Follow logs"
	@echo "  make docker-stop                      # Stop container"

## docker-stop: Stop and remove Docker container
docker-stop:
	@echo "$(BLUE)Stopping Docker container...$(NC)"
	@docker stop $(DOCKER_CONTAINER) 2>/dev/null || true
	@docker rm $(DOCKER_CONTAINER) 2>/dev/null || true
	@echo "$(GREEN)✓ Container stopped and removed$(NC)"

## docker-logs: Show Docker container logs
docker-logs:
	@docker logs -f $(DOCKER_CONTAINER)

## docker-shell: Open shell in running container
docker-shell:
	@docker exec -it $(DOCKER_CONTAINER) /bin/sh

## docker-clean: Remove Docker image and container
docker-clean: docker-stop
	@echo "$(BLUE)Removing Docker image...$(NC)"
	@docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "$(GREEN)✓ Docker image removed$(NC)"

## docker-compose-up: Start with Docker Compose (builds site in container)
docker-compose-up:
	@echo "$(BLUE)Starting with Docker Compose (building site in container)...$(NC)"
	@docker-compose up -d --build
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(GREEN)Visit: http://localhost:$(PORT)$(NC)"
	@echo "$(YELLOW)Note: Site was built inside Docker container$(NC)"

## docker-compose-down: Stop Docker Compose services
docker-compose-down:
	@echo "$(BLUE)Stopping Docker Compose services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

## docker-compose-logs: Show Docker Compose logs
docker-compose-logs:
	@docker-compose logs -f

## docker-compose-rebuild: Rebuild and restart Docker Compose services
docker-compose-rebuild:
	@echo "$(BLUE)Rebuilding Docker Compose services...$(NC)"
	@docker-compose up -d --build
	@echo "$(GREEN)✓ Services rebuilt and restarted$(NC)"
	@echo "$(YELLOW)Note: Site was rebuilt inside Docker container$(NC)"

## validate: Validate Hugo configuration
validate:
	@echo "$(BLUE)Validating Hugo configuration...$(NC)"
	@hugo config
	@echo "$(GREEN)✓ Configuration valid$(NC)"

## lint: Check for common issues
lint:
	@echo "$(BLUE)Checking for issues...$(NC)"
	@if [ ! -d "content" ]; then \
		echo "$(YELLOW)Warning: content/ directory not found$(NC)"; \
		echo "$(YELLOW)Run 'make content' to generate it$(NC)"; \
	fi
	@if [ ! -d "public" ]; then \
		echo "$(YELLOW)Warning: public/ directory not found$(NC)"; \
		echo "$(YELLOW)Run 'make build' to generate it$(NC)"; \
	fi
	@if [ ! -f "hugo.toml" ]; then \
		echo "$(RED)Error: hugo.toml not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Lint check complete$(NC)"

## test: Run basic tests
test: build
	@echo "$(BLUE)Running tests...$(NC)"
	@echo "  Checking if public/ exists..."
	@test -d public/ || (echo "$(RED)✗ public/ not found$(NC)" && exit 1)
	@echo "$(GREEN)  ✓ public/ exists$(NC)"
	@echo "  Checking if index.html exists..."
	@test -f public/index.html || (echo "$(RED)✗ index.html not found$(NC)" && exit 1)
	@echo "$(GREEN)  ✓ index.html exists$(NC)"
	@echo "  Checking if CSS exists..."
	@test -f public/css/style.css || (echo "$(RED)✗ CSS not found$(NC)" && exit 1)
	@echo "$(GREEN)  ✓ CSS exists$(NC)"
	@echo "  Checking if JS exists..."
	@test -f public/js/main.js || (echo "$(RED)✗ JS not found$(NC)" && exit 1)
	@echo "$(GREEN)  ✓ JS exists$(NC)"
	@echo "  Checking page count..."
	@PAGE_COUNT=$$(find public -name "index.html" | wc -l | tr -d ' '); \
	if [ $$PAGE_COUNT -lt 9 ]; then \
		echo "$(RED)✗ Expected at least 9 pages, found $$PAGE_COUNT$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)  ✓ Found $$(find public -name "index.html" | wc -l | tr -d ' ') pages$(NC)"
	@echo "$(GREEN)✓ All tests passed$(NC)"

## install: Check and install dependencies
install:
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v hugo >/dev/null 2>&1 || \
		(echo "$(RED)✗ Hugo not found$(NC)" && \
		echo "$(YELLOW)Install from: https://gohugo.io/installation/$(NC)" && \
		exit 1)
	@echo "$(GREEN)✓ Hugo $(shell hugo version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+')$(NC)"
	@command -v python3 >/dev/null 2>&1 || \
		(echo "$(RED)✗ Python3 not found$(NC)" && exit 1)
	@echo "$(GREEN)✓ Python $(shell python3 --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')$(NC)"
	@command -v docker >/dev/null 2>&1 || \
		echo "$(YELLOW)⚠ Docker not found (optional)$(NC)"
	@command -v docker >/dev/null 2>&1 && \
		echo "$(GREEN)✓ Docker $(shell docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')$(NC)" || true
	@echo "$(GREEN)✓ All required dependencies installed$(NC)"

## status: Show current status
status:
	@echo "$(BLUE)Site Status:$(NC)"
	@echo ""
	@echo "$(YELLOW)Content:$(NC)"
	@if [ -d "content" ]; then \
		echo "  $(GREEN)✓$(NC) Content directory exists ($$(ls -1 content/*.md 2>/dev/null | wc -l | tr -d ' ') files)"; \
	else \
		echo "  $(RED)✗$(NC) Content directory not found"; \
	fi
	@echo ""
	@echo "$(YELLOW)Built Site:$(NC)"
	@if [ -d "public" ]; then \
		echo "  $(GREEN)✓$(NC) Public directory exists ($$(find public -name "*.html" | wc -l | tr -d ' ') HTML files)"; \
		echo "  $(GREEN)✓$(NC) Size: $$(du -sh public | cut -f1)"; \
	else \
		echo "  $(RED)✗$(NC) Public directory not found"; \
	fi
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(DOCKER_CONTAINER)$$"; then \
		if docker ps --format '{{.Names}}' | grep -q "^$(DOCKER_CONTAINER)$$"; then \
			echo "  $(GREEN)✓$(NC) Container running"; \
			echo "  $(GREEN)✓$(NC) Port: $(PORT)"; \
		else \
			echo "  $(YELLOW)⚠$(NC) Container exists but not running"; \
		fi; \
	else \
		echo "  $(YELLOW)⚠$(NC) Container not found"; \
	fi
	@if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^$(DOCKER_IMAGE):$(DOCKER_TAG)$$"; then \
		echo "  $(GREEN)✓$(NC) Image exists"; \
	else \
		echo "  $(YELLOW)⚠$(NC) Image not found"; \
	fi

## all: Build everything (content, site, and Docker image)
all: build docker-build
	@echo ""
	@echo "$(GREEN)✓ All build tasks complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  make serve          # Serve locally"
	@echo "  make docker-run     # Run in Docker"
	@echo "  make dev            # Development mode"

## quick-docker: Quick start with Docker (recommended)
quick-docker:
	@echo "$(BLUE)🚀 Quick Docker Start$(NC)"
	@echo "$(YELLOW)Building and starting site in Docker...$(NC)"
	@docker-compose up -d --build
	@echo ""
	@echo "$(GREEN)✓ Site is running!$(NC)"
	@echo "$(GREEN)📍 Visit: http://localhost:$(PORT)$(NC)"
	@echo ""
	@echo "$(YELLOW)Useful commands:$(NC)"
	@echo "  docker-compose logs -f     # View logs"
	@echo "  make docker-stop           # Stop container"
	@echo "  make docker-compose-down   # Stop services"

## rebuild: Clean and rebuild everything
rebuild: clean all

## update: Update content from docs and rebuild
update:
	@echo "$(BLUE)Updating site...$(NC)"
	@$(MAKE) clean
	@$(MAKE) content
	@$(MAKE) hugo
	@echo "$(GREEN)✓ Site updated$(NC)"

## watch: Watch for changes and rebuild (requires fswatch or inotifywait)
watch:
	@echo "$(BLUE)Watching for changes...$(NC)"
	@echo "$(YELLOW)Use 'make dev' for Hugo's built-in live reload instead$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@while true; do \
		$(MAKE) build; \
		sleep 5; \
	done

## size: Show size of built site
size:
	@echo "$(BLUE)Site Size:$(NC)"
	@if [ -d "public" ]; then \
		echo ""; \
		echo "$(YELLOW)Total size:$(NC) $$(du -sh public | cut -f1)"; \
		echo ""; \
		echo "$(YELLOW)Breakdown:$(NC)"; \
		du -sh public/* | sort -hr | head -10; \
	else \
		echo "$(RED)Public directory not found. Run 'make build' first.$(NC)"; \
	fi

## urls: Show all URLs in the site
urls:
	@echo "$(BLUE)Site URLs:$(NC)"
	@if [ -d "public" ]; then \
		echo ""; \
		find public -name "index.html" | sed 's|public||' | sed 's|/index.html||' | sed 's|^|  http://localhost:$(PORT)|' | sort; \
		echo ""; \
	else \
		echo "$(RED)Public directory not found. Run 'make build' first.$(NC)"; \
	fi

## version: Show versions of tools
version:
	@echo "$(BLUE)Tool Versions:$(NC)"
	@echo ""
	@echo "$(YELLOW)Hugo:$(NC)"
	@hugo version || echo "$(RED)Not installed$(NC)"
	@echo ""
	@echo "$(YELLOW)Python:$(NC)"
	@python3 --version || echo "$(RED)Not installed$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@docker --version || echo "$(RED)Not installed$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker Compose:$(NC)"
	@docker-compose --version || echo "$(RED)Not installed$(NC)"

## info: Show detailed information
info: version status
	@echo ""
	@echo "$(BLUE)Configuration:$(NC)"
	@echo "  Docker Image:     $(DOCKER_IMAGE):$(DOCKER_TAG)"
	@echo "  Docker Container: $(DOCKER_CONTAINER)"
	@echo "  HTTP Port:        $(PORT)"
	@echo "  Hugo Dev Port:    $(HUGO_PORT)"
	@echo ""
	@echo "$(BLUE)Directories:$(NC)"
	@echo "  Content:  content/"
	@echo "  Public:   public/"
	@echo "  Themes:   themes/client-go-docs/"
	@echo ""
	@echo "$(BLUE)Quick Commands:$(NC)"
	@echo "  make build        # Build the site"
	@echo "  make serve        # Serve locally"
	@echo "  make dev          # Development mode"
	@echo "  make docker-run   # Run in Docker"
	@echo "  make help         # Show all commands"
