.PHONY: backend frontend dev update-db

backend:
	uv run uvicorn backend.main:app --reload

frontend:
	cd frontend && npm start

dev:
	$(MAKE) backend & $(MAKE) frontend & wait

update-db:
	uv run python -m backend.db.update_db
