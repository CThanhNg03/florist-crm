from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import florists as api_florists
from app.api.routes import orders as api_orders
from app.api.routes import tasks as api_tasks
from app.core.config import get_settings
from app.routers import auth, customers, health, orders, skus

TAGS_METADATA = [
    {
        "name": "health",
        "description": "Service liveness checks.",
    },
    {
        "name": "auth",
        "description": "Authentication and user session endpoints.",
    },
    {
        "name": "customers",
        "description": "Customer management endpoints.",
    },
    {
        "name": "skus",
        "description": "Product and template catalog endpoints.",
    },
    {
        "name": "orders",
        "description": "Order lifecycle management endpoints.",
    },
    {
        "name": "tasks",
        "description": "Task management endpoints.",
    },
    {
        "name": "florists",
        "description": "Florist directory endpoints.",
    },
]

def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(title="Florist CRM API", openapi_tags=TAGS_METADATA)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_router = APIRouter(prefix="/api")
    api_router.include_router(api_tasks.router)
    api_router.include_router(api_orders.router)
    api_router.include_router(api_florists.router)

    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(customers.router)
    application.include_router(skus.router)
    application.include_router(orders.router)
    application.include_router(api_router)

    application.mount(settings.media_url, StaticFiles(directory=settings.media_root), name="media")

    return application


app = create_app()
