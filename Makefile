.PHONY: dev test lint format up down logs migrate

dev:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	alembic upgrade head
