.PHONY: dev backend frontend install test lint

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r backend/requirements.txt
	cd frontend && npm install

backend:
	. .venv/bin/activate && uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0

dev:
	@echo "Start backend and frontend in separate terminals:"
	@echo "  make backend"
	@echo "  make frontend"

test:
	. .venv/bin/activate && pytest backend/tests -q

lint:
	. .venv/bin/activate && ruff check backend
	cd frontend && npm run lint
