# Makefile for GetScrapper

.PHONY: help install install-dev test test-unit test-integration test-cov lint format clean build docs

help: ## Show this help message
	@echo "GetScrapper - Web Scraping Tool"
	@echo "================================"
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