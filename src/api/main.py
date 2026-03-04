import os
import shutil
import structlog
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.core.logic.ingestion import ingest_document
from src.core.logic.retrieval import generate_answer
from src.api.schemas import IngestResponse, QueryRequest, QueryResponse

logger = structlog.get_logger()

app = FastAPI(title="SecureDoc-AI API")

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_file(file_path: str):
    """Utility to delete temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("temp_file_removed", path=file_path)
    except Exception as e:
        logger.error("cleanup_failed", path=file_path, error=str(e))

@app.get("/")
async def root():
    return {"message": "SecureDoc-AI API is running"}

@app.post("/ingest/file", response_model=IngestResponse)
async def upload_file(file: UploadFile = File(...)):
    """Accepts a PDF file, processes it, and stores in Qdrant."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(TEMP_DIR, file.filename)
    
    try:
        # Save file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("file_uploaded", filename=file.filename)
        
        # Process document
        result = await ingest_document(file_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
        
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_file(file_path)

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """Processes a user query and returns an answer with citations."""
    try:
        logger.info("chat_request", query=request.query)
        result = await generate_answer(request.query)
        return result
    except Exception as e:
        logger.error("chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")
