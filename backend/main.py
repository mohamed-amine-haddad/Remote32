from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import backend.models  
from backend.database import create_db_and_tables, engine
from backend.routers.auth import router as auth_router
from backend.services.config_loader import load_all_configs, validate_configs
from sqlmodel import Session
from backend.routers.devices import router as devices_router
from backend.routers.applications import router as applications_router
from backend.routers.bookings import router as bookings_router
from backend.routers.application_sessions import router as application_sessions_router

# TO BE TESTED

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    configs = load_all_configs()
    with Session(engine) as db:
        validate_configs(configs, db)
    app.state.configs = configs
    # Stable integer ID → json_path mapping (order matches dict insertion order)
    app.state.configs_ids = {i + 1: path for i, path in enumerate(configs.keys())}
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
app.include_router(devices_router)
app.include_router(applications_router)
app.include_router(bookings_router)
app.include_router(application_sessions_router)


@app.get("/")
def root():
    return {"message": "Remote32 API is running"}
