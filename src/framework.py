from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from .infra.db import asyncsessionmanager
from .settings import AppSettings, get_settings


class Framework:

    def __init__(
        self,
        settings: AppSettings,
        init_db: bool,
        router: APIRouter | None = None,
        db_url: str | None = None,
    ):
        if init_db:
            # db_str = settings.DATABASE_URI if settings.DATABASE_URI != "" else db_url
            db_str = db_url if db_url else settings.DATABASE_URI
            asyncsessionmanager.init(
                db_str,
                settings.set_engine_args,
                settings.set_session_args,
            )

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("Welcome 🛬")
            print(f"Application v{app.version} started elegantly!")
            yield
            if asyncsessionmanager._engine is not None:
                await asyncsessionmanager.close()
            get_settings.cache_clear()
            print(f"Application v{app.version} shut down gracefully!")

        self.__app = FastAPI(lifespan=lifespan, **settings.set_app_attributes)  # type: ignore
        self.__add_routes(router=router)

    def __add_routes(self, router: APIRouter | None):
        if router:
            self.__app.include_router(router=router)

    def __call__(self) -> FastAPI:
        return self.__app
