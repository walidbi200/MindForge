.PHONY: dev test lint format migrate verify build down

dev:
	docker compose up --build

down:
	docker compose down

test:
	docker compose exec api uv run pytest

lint:
	docker compose exec api uv run ruff check .

format:
	docker compose exec api uv run ruff format .

migrate:
	docker compose exec api uv run alembic upgrade head

verify: lint test
	@echo "Verification complete."

build:
	docker compose build
