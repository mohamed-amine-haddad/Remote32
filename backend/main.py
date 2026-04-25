from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import backend.models  # registers ALL table classes into SQLModel.metadata
from backend.database import create_db_and_tables, engine
from backend.routers.auth import router as auth_router
from backend.services.config_loader import load_all_configs, validate_configs
from sqlmodel import Session

# TO BE TESTED

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as db:
        validate_configs(load_all_configs(), db)
    yield


app = FastAPI(title="Remote32 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,                   # required so cookies are forwarded
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Remote32 API is running"}
