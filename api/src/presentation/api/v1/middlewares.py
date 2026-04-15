from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from bootstrap.config.app import AppConfig


class ApiKEyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        app_config = request.state.di_container.resolve(AppConfig)

        api_key = request.headers.get("X-API-Key")
        if api_key != app_config.api_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

        return await call_next(request)

