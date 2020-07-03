help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	poetry install

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} \; || true

dev: ## Start the development environment
	nodemon --ext py -x python server.py

tdd: ## Run tests with a watcher
	LOGGING_LEVEL=CRITICAL ptw -- -sx

test: ## Run test suite
	pytest --cov

lint: ## Run lint check
	black --check .
