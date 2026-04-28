import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ...core.exceptions import ApplicationError

error_code = {
    ApplicationError: 500,
}


def get_http_error_response(
    err: ApplicationError,
) -> JSONResponse:
    err_type = type(err)
    err_http_code = error_code[err_type]

    return JSONResponse(
        status_code=err_http_code,
        content={},
    )


async def app_exception_handler(
    _request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    return get_http_error_response(exc)


def include_exception_handlers(app: FastAPI) -> None:
    logging.debug("Exception handlers was included.")
    app.add_exception_handler(ApplicationError, app_exception_handler)
