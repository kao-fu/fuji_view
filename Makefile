# Variables
FRONTEND_DIR := frontend
BACKEND_DIR := backend
PYTHON := python3
PIP := pip3
VENV := .env
FRONTEND_DEV_SERVER := $(FRONTEND_DIR)/node_modules/.bin/vite

.PHONY: run-frontend
run-frontend:
    # cd $(FRONTEND_DIR) && $(FRONTEND_DEV_SERVER)
	cd $(FRONTEND_DIR) && npm run dev

.PHONY: run-backend
run-backend:
	cd $(BACKEND_DIR) && uvicorn main:app --reload