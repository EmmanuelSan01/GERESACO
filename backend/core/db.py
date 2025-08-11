import os
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Example (MySQL): mysql+pymysql://user:password@host:3306/database_name"
        )
    return url


# Create a synchronous engine (recommended for SQLModel by default)
engine = create_engine(get_database_url(), echo=False)


def create_db_and_tables() -> None:
    # Imports intentionally inside the function to avoid circular imports.
    from backend.models.users.UsersModel import User
    from backend.models.rooms.RoomsModel import Room

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
