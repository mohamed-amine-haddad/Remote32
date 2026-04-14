from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Remote32 API", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Remote32 API is running"}
