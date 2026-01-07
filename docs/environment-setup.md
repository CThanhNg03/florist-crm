# Environment Setup Guide

This guide explains how to configure environment variables for on-prem/local deployments and AWS-hosted deployments. The API reads settings from environment variables (or a `.env` file locally) using `pydantic-settings`.

## Environment variables used by the API

| Variable | Required | Purpose | Example |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection string. | `postgresql://postgres:postgres@localhost:5432/postgres` |
| `JWT_SECRET` | Yes | Secret used to sign JWTs. | `change-me` |
| `JWT_EXPIRES_MIN` | No | JWT expiration in minutes (default 60). | `60` |
| `CORS_ORIGINS` | No | Comma-separated list of allowed origins (default `*`). | `https://app.example.com,https://admin.example.com` |
| `MEDIA_ROOT` | No | Local path for media storage (default `media`). | `media` |
| `MEDIA_URL` | No | URL prefix for serving media (default `/media`). | `/media` |

> **Note:** The backend does not require AWS credentials directly. If your frontend requests presigned URLs, configure that in your frontend or a separate signing service.

## Local/on-prem setup (Uvicorn or Docker)

1. Copy the example file and update values:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with the correct database connection string and JWT secret.
3. Choose one of the following runtime options:

### Option A: Docker Compose (recommended for local dev)

```bash
docker compose up --build
```

### Option B: Run with Uvicorn on a host

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## AWS setup

When deploying on AWS (Lambda, ECS, or EC2), set environment variables in the service configuration rather than relying on a `.env` file.

### Lambda

1. In the Lambda console, open **Configuration → Environment variables**.
2. Add the variables from the table above.
3. Store secrets like `JWT_SECRET` in AWS Secrets Manager or SSM Parameter Store and reference them in your deployment pipeline.

### ECS/EC2

1. Add environment variables to your task definition (ECS) or systemd/unit file (EC2).
2. Use IAM roles and AWS Secrets Manager/SSM to avoid hardcoding secrets.

### Database connectivity

- Use an RDS instance or another PostgreSQL-compatible database reachable from your AWS runtime.
- If using Lambda, ensure the function has VPC access to the database and consider RDS Proxy for connection pooling.
