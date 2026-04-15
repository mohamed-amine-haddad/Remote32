from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_db_and_tables
from backend.routers.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Remote32 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,                   # required so cookies are forwarded
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Remote32 API is running"}
