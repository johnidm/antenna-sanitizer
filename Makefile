.DEFAULT_GOAL := help
.PHONY: help install sync run lint lint-fix format format-check check clean upgrade

UV ?= uv

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Create the venv and install all dependencies (incl. dev)
	$(UV) sync

sync: ## Sync the venv exactly with uv.lock
	$(UV) sync --locked

run: ## Run the TUI
	$(UV) run antenna-sanitizer

lint: ## Lint with Ruff
	$(UV) run ruff check .

lint-fix: ## Lint with Ruff and apply safe fixes
	$(UV) run ruff check --fix .

format: ## Format code with Ruff
	$(UV) run ruff format .

format-check: ## Verify formatting without writing changes
	$(UV) run ruff format --check .

check: lint format-check ## Run all checks (CI entry point)

upgrade: ## Upgrade locked dependencies
	$(UV) lock --upgrade
	$(UV) sync

clean: ## Remove caches
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
