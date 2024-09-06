from itertools import zip_longest
from typing import Annotated

from fastapi import FastAPI, Depends
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession
)
from sqlalchemy.pool import StaticPool

from src.infra.db import get_async_db, asyncsessionmanager
from src.models.models import Base

from src.framework import Framework
from src.settings import settings
from src.routes.bankslip import router

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_database():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        future=True,
        echo=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    asyncsessionmanager.init(
        host="sqlite+aiosqlite:///:memory:",
        engine_args={"echo": True},
        session_args={"expire_on_commit": False},
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(setup_test_database):
    async with asyncsessionmanager.session() as session:
        yield session


@pytest_asyncio.fixture()
async def application(session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    test_dep = Annotated[AsyncSession, Depends(session)]
    # test_app = Framework(router=router, settings=settings, init_db=False)()
    test_app = FastAPI()
    test_app.include_router(router)
    test_app.dependency_overrides[get_async_db] = lambda: test_dep
    return test_app


@pytest.fixture
def valid_bankslip_request():
    columns = [
        "name",
        "government_id",
        "email",
        "debt_amount",
        "debt_due_date",
        "debt_id",
    ]
    values = [
        "Elijah Santos",
        "9558",
        "janet95@example.com",
        7811,
        "2024-01-19",
        "ea23f2ca-663a-4266-a742-9da4c9f4fcb3",
    ]
    return dict(zip_longest(columns, values))
