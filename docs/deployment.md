# Deployment Guide: FastAPI & AWS Lambda

This project is structured with Clean Architecture so the same application wiring runs on both Uvicorn and AWS Lambda (via Mangum). Use this guide to configure environments, run locally, and deploy to Lambda while keeping API contracts unchanged.

## Prerequisites

- Python 3.11+
- PostgreSQL database reachable from your runtime
- AWS account with permissions for Lambda, API Gateway, ECR (if using container images), and S3
- Required environment variables (can come from `.env`, Docker Compose, Lambda configuration, or your CI/CD system):
  - `DATABASE_URL` – PostgreSQL connection string
  - `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (or IAM role when on AWS)
  - `S3_BUCKET` (used by the frontend when requesting presigned URLs)
  - Any SMTP or other integration settings your deployment needs

## Running with Uvicorn (local or on-prem)

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Export environment variables (or create a `.env` file loaded by `pydantic-settings`).
4. Apply database migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

The FastAPI docs are available at `http://localhost:8000/docs`. All request handlers delegate to use cases; no code changes are needed to switch between runtimes.

## Deploying to AWS Lambda (API Gateway)

The Lambda entrypoint is `app.lambda_handler.handler` which wraps the same FastAPI app with `Mangum`. You can deploy either a zipped function or a container image.

### Option A: Zip-based Lambda

1. Build a deployment package:
   ```bash
   rm -rf build package
   python -m venv build
   source build/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   deactivate
   mkdir -p package
   cp -R app build/lib/python*/site-packages/* package/
   cp -R app package/
   cd package && zip -r ../function.zip . && cd ..
   ```
2. Create the Lambda function (runtime Python 3.11) with handler `app.lambda_handler.handler` and upload `function.zip`.
3. Configure environment variables (same as local) and connect the function to your database (e.g., via VPC + RDS).
4. Create an HTTP API Gateway and integrate it with the Lambda function. No additional adapters are required because Mangum translates API Gateway events to ASGI.

### Option B: Container image Lambda

1. Build and push the image to ECR:
   ```bash
   aws ecr create-repository --repository-name florist-crm || true
   docker build -t florist-crm .
   docker tag florist-crm:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/florist-crm:latest
   aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
   docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/florist-crm:latest
   ```
2. Create a Lambda function from the image and set the command to the default container entrypoint. The handler is still `app.lambda_handler.handler` inside the image.
3. Configure environment variables and VPC access for the database as needed.
4. Attach API Gateway to the function.

### Database connections and performance

- SQLAlchemy engine/session creation happens once in `app.db.session`, so connections can be reused across Lambda invocations when the execution environment is warm.
- Use RDS Proxy if you expect high concurrency to smooth connection bursts from cold starts.

## Image uploads

The backend no longer accepts multipart uploads. The frontend must upload task completion images directly to S3 using presigned URLs and then send the resulting object key or URL in the API payload (e.g., `completionProofUrl`). Only the URL/key is stored in the database.

## Troubleshooting

- **Cold starts**: For latency-sensitive endpoints, prefer provisioned concurrency on Lambda or run the same app with Uvicorn on a traditional host.
- **Migrations on AWS**: Run Alembic migrations from CI/CD or a one-off task/container before switching traffic to a new environment.
- **CORS**: Configure `CORS_ORIGINS` (if present in settings) to include your frontend domain when deploying behind API Gateway.
