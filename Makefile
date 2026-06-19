# Repository commands

.DEFAULT_GOAL := help

PYTHON ?= python3.11
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
RUFF := $(VENV)/bin/ruff
TEST_FILE := bible/tests/bible_test.py
LINT_TARGETS := bible
REQ_FILE := bible/requirements.txt

.PHONY: help venv install fmt lint check test clean

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_.-]+:.*## / {printf "%-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Create the repo-local virtual environment with Python 3.11
	$(PYTHON) -m venv $(VENV)

install: venv ## Install project dependencies into .venv
	$(VENV_PIP) install -r $(REQ_FILE)

fmt: ## Format Python code with Ruff
	$(RUFF) format $(LINT_TARGETS)

lint: ## Lint Python code with Ruff
	$(RUFF) check $(LINT_TARGETS)

check: lint test ## Run lint and tests

test: ## Run the test suite from the repo root
	$(VENV_PYTHON) -m pytest $(TEST_FILE)

clean: ## Remove Python caches
	find bible -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +

