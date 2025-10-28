.PHONY: dev migrate

DEV_COMPOSE=docker compose

dev:
$(DEV_COMPOSE) up --build

migrate:
$(DEV_COMPOSE) run --rm api alembic upgrade head
