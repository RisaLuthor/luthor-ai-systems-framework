from __future__ import annotations

import os
from fastapi import Request
from fastapi.responses import JSONResponse


PUBLIC_PATH_PREFIXES = ("/health", "/docs", "/openapi.json", "/project", "/")


def _is_public(path: str) -> bool:
    return path == "/" or any(path.startswith(p) for p in PUBLIC_PATH_PREFIXES)


def _get_token() -> str | None:
    # If not set, auth is effectively disabled (dev-friendly)
    return os.getenv("LAF_API_TOKEN")


async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if _is_public(path):
        return await call_next(request)

    token = _get_token()
    if not token:
        return await call_next(request)

    provided = request.headers.get("X-LAF-Token")
    if provided != token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized. Provide X-LAF-Token."},
        )

    return await call_next(request)
