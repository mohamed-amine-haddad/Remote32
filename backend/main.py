from fastapi import FastAPI

app = FastAPI(title="Remote32 API")

@app.get("/")
def root():
    return {"message": "Remote32 API is running"}