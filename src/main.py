from fastapi import FastAPI

from .framework import Framework
from .router import router
from .settings import settings


def initialize_application() -> FastAPI:
    return Framework(router=router, settings=settings, init_db=True)()


app = initialize_application()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
