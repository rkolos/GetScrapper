# Makefile for Universal HTML Renderer

.PHONY: help install install-dev test test-unit test-integration test-cov lint format clean build docs api-start api-stop api-test api-logs

help: ## Show this help message
	@echo "Universal HTML Renderer - API Service"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install GetScrapper
	pip install -e .

install-dev: ## Install GetScrapper in development mode with all dependencies
	pip install -e ".[dev]"

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	pytest --cov=getscrapper --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without slow tests
	pytest -m "not slow"

lint: ## Run linting
	flake8 getscrapper tests
	mypy getscrapper

format: ## Format code
	black getscrapper tests
	isort getscrapper tests

format-check: ## Check code formatting
	black --check getscrapper tests
	isort --check-only getscrapper tests

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package
	python setup.py sdist bdist_wheel

docs: ## Generate documentation
	@echo "Documentation generation not implemented yet"

check: format-check lint test ## Run all checks (format, lint, test)

ci: ## Run CI pipeline
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test-cov

dev-setup: ## Setup development environment
	pip install -e ".[dev]"
	pre-commit install

# Example usage commands
example-basic: ## Run basic scraping example
	python -m getscrapper.cli scrape https://httpbin.org/html

example-json: ## Run JSON scraping example
	python -m getscrapper.cli scrape https://httpbin.org/json --parser json

example-multiple: ## Run multiple URLs scraping example
	python -m getscrapper.cli scrape-multiple https://httpbin.org/html https://httpbin.org/json

example-config: ## Generate example configuration
	python -m getscrapper.cli config --output example_config.json

# Docker commands (if needed)
docker-build: ## Build Docker image
	docker build -t getscrapper .

docker-test: ## Run tests in Docker
	docker run --rm getscrapper make test

# Release commands
release-patch: ## Release patch version
	bump2version patch
	git push --tags
	git push

release-minor: ## Release minor version
	bump2version minor
	git push --tags
	git push

release-major: ## Release major version
	bump2version major
	git push --tags
	git push

# API Service commands
api-start: ## Start API server with Docker Compose
	docker-compose up -d api-server

api-stop: ## Stop API server
	docker-compose down

api-restart: ## Restart API server
	docker-compose restart api-server

api-logs: ## Show API server logs
	docker-compose logs -f api-server

api-test: ## Test API server
	python test_api.py

api-examples: ## Run API examples
	python api_examples.py

api-dev: ## Start API server in development mode
	python api_server.py

# CLI commands
cli-help: ## Show CLI help
	python cli.py --help

cli-scrape: ## Scrape single URL (usage: make cli-scrape URL=https://example.com)
	python cli.py $(URL)

cli-batch: ## Batch scrape URLs from file (usage: make cli-batch FILE=urls.txt)
	python cli.py --batch $(FILE)

# Docker commands
docker-build: ## Build Docker image
	docker-compose build

docker-clean: ## Clean Docker containers and images
	docker-compose down --rmi all --volumes --remove-orphans

# Development commands
dev-install: ## Install development dependencies
	pip install -r requirements.txt

dev-test: ## Run all tests
	python test_api.py
	python test_system.py