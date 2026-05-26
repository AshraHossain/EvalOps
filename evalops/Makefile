SHELL := /bin/sh

up:
	docker-compose -f infrastructure/docker/docker-compose.yml up -d

migrate:
	cd backend && ./.venv/Scripts/python -m alembic upgrade head

run:
	cd backend && ./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000 --loop asyncio

test:
	cd backend && ./.venv/Scripts/python -m pytest -q
