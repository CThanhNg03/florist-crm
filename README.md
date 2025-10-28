# Florist CRM API

Florist CRM is a FastAPI-powered backend for managing florist shop operations. The service uses PostgreSQL via SQLAlchemy and provides JWT-based authentication with role support.

## Getting started

1. Copy `.env.example` to `.env` and adjust the values as needed.
2. Build and start the stack:
   ```bash
   docker compose up --build
   ```
3. Apply database migrations in another terminal:
   ```bash
   make migrate
   ```
4. (Optional) Seed default users:
   ```bash
   docker compose run --rm api python scripts/seed.py
   ```

The API will be available at <http://localhost:8000>. Interactive API docs live at <http://localhost:8000/docs>.

## Default users

The seed script creates the following accounts (password `changeme`):

| Role    | Username |
|---------|----------|
| ADMIN   | admin    |
| SALE    | sales    |
| FLORIST | florist  |

## Makefile commands

- `make dev` – build and start the Docker Compose stack.
- `make migrate` – run Alembic migrations inside the API container.

## Tech stack

- FastAPI + Uvicorn
- SQLAlchemy 2.0 + Alembic
- PostgreSQL
- Pydantic v2 + pydantic-settings
- JWT authentication with passlib for password hashing
