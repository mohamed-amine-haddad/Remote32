from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

# Absolute path so the DB is always created inside backend/,
# regardless of which directory uvicorn is launched from.
_DB_PATH = Path(__file__).parent / "remote32.db"
DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    import models  # registers Board, User, DeviceSession, ApplicationSession into metadata
    create_db_and_tables()
    print(f"Database created at: {_DB_PATH}")
