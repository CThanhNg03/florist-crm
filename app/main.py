from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import auth, health

TAGS_METADATA = [
    {
        "name": "health",
        "description": "Service liveness checks.",
    },
    {
        "name": "auth",
        "description": "Authentication and user session endpoints.",
    },
]

settings = get_settings()

app = FastAPI(title="Florist CRM API", openapi_tags=TAGS_METADATA)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
