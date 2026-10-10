import logging

from fastapi import FastAPI

from ..endpoints.root import router as root_router


def include_routers(app: FastAPI) -> None:
    app.include_router(root_router)
    logging.debug("Routers was included.")
