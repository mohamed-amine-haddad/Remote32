from sqlmodel import create_engine, Session

DATABASE_URL = "sqlite:///./remote32.db"

# Create the connection to the SQLite file remote32.db
engine = create_engine(DATABASE_URL)

# Creates a database session and hands it to FastAPI endpoints
def get_session():
    with Session(engine) as session:
        yield session
