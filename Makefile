# Variables
PYTHON = python
PIP = pip
DOCKER_IMAGE = astro-api

.PHONY: help install run test docker-build docker-run clean lint

help: ## Display this help message with available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies from requirements.txt
	$(PIP) install -r requirements.txt

run: ## Start the FastAPI server locally
	$(PYTHON) -m app.api

test: ## Run all tests (Unit and API) with verbose output
	pytest tests/ -v -s

docker-build: ## Build the Docker image for the application
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run the application in a Docker container using .env file
	# Use --env-file to pass environment variables to the container
	docker run -p 8000:8000 --env-file .env $(DOCKER_IMAGE)

lint: ## Check code for style and linting errors using Ruff
	ruff check .

clean: ## Remove temporary Python files, cache, and logs
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete
	rm -rf .pytest_cache
	rm -rf logs/*.log