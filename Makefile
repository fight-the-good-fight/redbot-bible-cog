# Repository commands
#
# Redbot 3.5.1 requires Python < 3.12, so keep the local venv on 3.11.

.DEFAULT_GOAL := help

PYTHON ?= python3.11
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
RUFF := $(VENV)/bin/ruff
TEST_DIR := bible/tests
PYTEST_COV_ARGS := --cov=bible --cov-report=term-missing
LINT_TARGETS := bible
REQ_FILE := bible/requirements.txt

.PHONY: help venv install setup fmt lint check test coverage build-index clean

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_.-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build-index: ## Build the bundled SQLite Bible search index
	$(VENV_PYTHON) -m bible.build_search_index --source-dir bible/data --output bible/search_index.sqlite


venv: ## Create the repo-local virtual environment with Python 3.11
	$(PYTHON) -m venv $(VENV)

install: venv ## Install project dependencies into .venv
	$(VENV_PIP) install -r $(REQ_FILE)

setup: install ## Alias for install

fmt: ## Format Python code with Ruff
	$(RUFF) format $(LINT_TARGETS)

lint: ## Lint Python code with Ruff
	$(RUFF) check $(LINT_TARGETS)

check: lint test ## Run lint and tests

test: ## Run the test suite from the repo root
	$(VENV_PYTHON) -m pytest $(TEST_DIR) $(PYTEST_COV_ARGS)

coverage: test ## Run tests with coverage output


clean: ## Remove Python caches
	find bible -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +

