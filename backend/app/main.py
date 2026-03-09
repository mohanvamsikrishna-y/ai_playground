from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .dependencies import get_registry
from .routers import auth, chat, compare, config, models, ollama


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
        allow_origins=settings.get_allowed_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(models.router)
    app.include_router(compare.router)
    app.include_router(chat.router)
    app.include_router(config.router)
    app.include_router(ollama.router)
    app.include_router(auth.router)
    return app


app = create_app()

