from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///./remote32.db"

# Create the connection to the SQLite file remote32.db
engine = create_engine(DATABASE_URL)

# Reads all SQLModel classes and creates the corresponding tables in the database if they don't exist yet
def create_db():
    SQLModel.metadata.create_all(engine)

# Creates a database session and hands it to FastAPI endpoints
def get_session():
    with Session(engine) as session:
        yield session
