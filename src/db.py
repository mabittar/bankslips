import contextlib
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine, Connection
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


class DatabaseSessionManager:
    def __init__(self):
        self._engine: Engine | None = None
        self._sessionmaker: sessionmaker | None = None

    def init(self, host: str, engine_args: dict, session_args: dict):
        self._engine = create_engine(host, future=True, **engine_args)
        self._sessionmaker = sessionmaker(
            autocommit=False, bind=self._engine, class_=Session, **session_args
        )

    def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def connect(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def session(self):
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_all(self, connection: Connection):
        Base.metadata.create_all(connection)

    def drop_all(self, connection: Connection):
        Base.metadata.drop_all(connection)


sessionmanager = DatabaseSessionManager()


def get_db():
    with sessionmanager.session() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
