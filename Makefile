help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	@[ -n "${VIRTUAL_ENV}" ] || (echo "ERROR: This should be run from a virtualenv" && exit 1)
	pip install -r requirements.txt

.PHONY: requirements.txt
requirements.txt: ## Regenerate requirements.txt
	pip-compile requirements.in > $@

dev: ## Start the development environment
	nodemon --ext py -x python server.py

tdd: ## Run tests with a watcher
	nodemon --ext py -x sh -c "pytest -sx || true"

test: ## Run test suite
	pytest --cov
