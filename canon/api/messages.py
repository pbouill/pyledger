from typing import Literal

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

MessageLevel = Literal["info", "success", "warning", "error"]


def set_message_headers(
    response: Response, text: str, level: MessageLevel = "info"
) -> None:
    """Attach message headers to a Response so frontend can show toasts."""
    response.headers["X-App-Message"] = text
    response.headers["X-App-Message-Level"] = level


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ensure HTTPException responses include the message header and structured body.

    Signature uses Exception to match Starlette's handler typing; we check instance type
    at runtime and re-raise if necessary.
    """
    if not isinstance(exc, HTTPException):
        raise exc
    text = str(exc.detail or "")
    content = {"detail": exc.detail}
    headers = {"X-App-Message": text, "X-App-Message-Level": "error"}
    return JSONResponse(status_code=exc.status_code, content=content, headers=headers)
