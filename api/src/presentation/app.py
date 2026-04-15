from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

from fastapi import FastAPI, APIRouter

from bootstrap.config.app import AppConfig
from bootstrap.config.pg import PgConfig
from bootstrap.config.rmq import RmqConfig
from infrastructure.di import DIContainer
from infrastructure.di import DIContainerFactory
from presentation.api.v1.middlewares import ApiKEyMiddleware
from presentation.api.v1.routes import router


class State(TypedDict):
    di_container: DIContainer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    di_container_factory = DIContainerFactory(
        app_config=AppConfig(),
        pg_config=PgConfig(),
        rmq_config=RmqConfig()
    )
    di_container = di_container_factory.build_di_container()
    yield State(di_container=di_container)


def init_app() -> FastAPI:
    app_config = AppConfig()
    app = FastAPI(
        # openapi_url=None,
        redoc_url=None,
        # docs_url=None,
        debug=app_config.debug,
        lifespan=lifespan
    )
    v1_router = APIRouter(
        prefix='/api/v1',
    )
    v1_router.include_router(router)
    app.include_router(v1_router)

    app.add_middleware(ApiKEyMiddleware)

    return app
