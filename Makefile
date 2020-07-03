help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	@[ -n "${VIRTUAL_ENV}" ] || (echo "ERROR: This should be run from a virtualenv" && exit 1)
	pip install -r requirements.txt

.PHONY: requirements.txt
requirements.txt: ## Regenerate requirements.txt
	pip-compile requirements.in > $@

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} \; || true

dev: ## Start the development environment
	nodemon --ext py -x python server.py

tdd: ## Run tests with a watcher
	LOGGING_LEVEL=CRITICAL ptw -- -sx

test: ## Run test suite
	pytest --cov
