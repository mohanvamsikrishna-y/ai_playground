from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .dependencies import get_registry
from .routers import compare, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry = get_registry()
    yield
    await registry.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="AI Model Comparison Playground", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(models.router)
    app.include_router(compare.router)
    return app


app = create_app()

