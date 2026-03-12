.PHONY: install frontend-install frontend-build frontend-dev backend-dev ingest lint format

# ── Install ──────────────────────────────────────────────

install: frontend-install
	poetry install

# ── Frontend ──────────────────────────────────────────────

frontend-install:
	cd frontend && npm install

frontend-build: frontend-install
	cd frontend && npm run build

frontend-dev:
	cd frontend && npm start

# ── Backend ───────────────────────────────────────────────

backend-dev:
	poetry run uvicorn backend.main:app --reload

# ── Ingestion ─────────────────────────────────────────────
# Usage:
#   make ingest                          # all years
#   make ingest YEAR=2024                # single year
#   make ingest YEAR=2024 ROUND=1        # single round

ingest:
	poetry run python3 -m backend.db.ingest $(if $(YEAR),--year $(YEAR)) $(if $(ROUND),--round $(ROUND))

# ── Linting ───────────────────────────────────────────────

lint:
	poetry run ruff check backend/

format:
	poetry run ruff format backend/
