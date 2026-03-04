from fastapi import FastAPI
from src.core.config import settings

app = FastAPI(title="SecureDoc-AI API")

@app.get("/")
async def root():
    return {"message": "SecureDoc-AI API is running", "collection": settings.COLLECTION_NAME}
