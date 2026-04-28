from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from ..core.config import settings
from ..core.di.container import get_async_container
from .exceptions import include_exception_handlers
from .v1.routes import include_routers


@asynccontextmanager
async def lifespan(fast_app: FastAPI) -> AsyncIterator[None]:
    yield
    await fast_app.state.dishka_container.close()


fast_app = FastAPI(
    title="JabBot API",
    lifespan=lifespan,
    root_path="/api",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    # version=app.__version__,
)


def run() -> None:
    container = get_async_container()

    setup_dishka(container=container, app=fast_app)

    include_routers(fast_app)
    include_exception_handlers(fast_app)

    uvicorn.run(
        fast_app,
        port=settings.get("api_port"),
        host=settings.get("api_host"),
        access_log=settings.get("api_enable_access_log"),
        log_config=None,
    )
