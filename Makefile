.DEFAULT_GOAL := help

BACKEND := backend
FRONTEND := frontend
VENV := $(BACKEND)/.venv

# Preferred ports. If they are busy, the next free port is used automatically.
PREFERRED_BACKEND_PORT ?= 8000
PREFERRED_FRONTEND_PORT ?= 5173
BACKEND_PORT ?= $(shell python3 $(CURDIR)/scripts/free_port.py $(PREFERRED_BACKEND_PORT))
FRONTEND_PORT ?= $(shell python3 $(CURDIR)/scripts/free_port.py $(PREFERRED_FRONTEND_PORT))
# Freeze the auto-selected values so every line in a recipe uses the same port.
BACKEND_PORT := $(BACKEND_PORT)
FRONTEND_PORT := $(FRONTEND_PORT)
API_ORIGIN := http://127.0.0.1:$(BACKEND_PORT)

.PHONY: help setup install install-backend install-frontend env migrate migration downgrade reset-db backend frontend dev test build check clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: install env migrate ## First-time setup: dependencies, .env, database

install: install-backend install-frontend ## Install backend and frontend dependencies

install-backend: ## Create .venv and install Python dependencies (uses uv)
	cd $(BACKEND) && uv venv --python 3.12 .venv
	cd $(BACKEND) && uv pip install --python .venv/bin/python -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd $(FRONTEND) && npm install

env: $(BACKEND)/.env ## Create backend/.env from the example if missing

$(BACKEND)/.env:
	cp $(BACKEND)/.env.example $(BACKEND)/.env

migrate: $(BACKEND)/.env ## Apply all pending database migrations
	cd $(BACKEND) && .venv/bin/alembic upgrade head

migration: $(BACKEND)/.env ## Create a migration: make migration m="description"
	@test -n "$(m)" || (echo 'Usage: make migration m="description"'; exit 1)
	cd $(BACKEND) && .venv/bin/alembic revision --autogenerate -m "$(m)"

downgrade: ## Roll back the last migration
	cd $(BACKEND) && .venv/bin/alembic downgrade -1

reset-db: ## Delete the SQLite database and re-run migrations (loses data)
	rm -f $(BACKEND)/finishline.db
	$(MAKE) migrate

backend: migrate ## Run the API with auto-reload
	@echo "API: http://localhost:$(BACKEND_PORT)/api"
	cd $(BACKEND) && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --reload --port $(BACKEND_PORT)

frontend: ## Run the Vite dev server (proxies /api to the backend)
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)  (API proxy: $(API_ORIGIN))"
	cd $(FRONTEND) && VITE_API_PROXY_TARGET=$(API_ORIGIN) npm run dev -- --port $(FRONTEND_PORT)

dev: migrate ## Run backend and frontend together (Ctrl+C stops both)
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)  |  API: http://localhost:$(BACKEND_PORT)/api"
	@trap 'kill 0' EXIT INT TERM; \
	( cd $(BACKEND) && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --reload --port $(BACKEND_PORT) ) & \
	( cd $(FRONTEND) && VITE_API_PROXY_TARGET=$(API_ORIGIN) npm run dev -- --port $(FRONTEND_PORT) ) & \
	wait

test: ## Run backend tests
	cd $(BACKEND) && .venv/bin/python -m pytest -q

build: ## Type-check and build the frontend
	cd $(FRONTEND) && npm run build

check: test build ## Run tests and build

clean: ## Remove build and test artifacts (keeps the database)
	rm -rf $(FRONTEND)/dist $(BACKEND)/.pytest_cache
	find $(BACKEND) -path $(BACKEND)/.venv -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
