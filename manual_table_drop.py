import logging

from sqlalchemy import create_engine

from src.models import Base

logger = logging.getLogger()
db_url = "sqlite:///./sql_app.db"


def migrate_tables() -> None:
    logger.info("Starting to migrate")

    engine = create_engine(db_url)
    with engine.begin() as conn:
        Base.metadata.drop_all(conn)

    logger.info("Done migrating")


if __name__ == "__main__":
    migrate_tables()
