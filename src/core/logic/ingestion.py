import structlog
import uuid
from src.services.pdf_service import PDFProcessor
from src.services.qdrant_service import VectorStoreService
from src.utils.pii_masker import mask_pii

logger = structlog.get_logger()

async def ingest_document(file_path: str) -> dict:
    """
    Orchestrates the ingestion pipeline:
    Load -> Mask PII -> Split -> Store.
    """
    task_id = str(uuid.uuid4())
    logger.info("starting_ingestion", file=file_path, task_id=task_id)
    
    try:
        # 1. Load & Split (PDFProcessor handles ADR-003 metadata)
        processor = PDFProcessor()
        chunks = processor.load_and_split(file_path)
        
        # 2. Mask PII in each chunk
        for chunk in chunks:
            chunk.page_content = mask_pii(chunk.page_content)
            
        # 3. Store in Vector Database
        vector_service = VectorStoreService()
        vector_service.upsert_documents(chunks)
        
        logger.info("ingestion_complete", task_id=task_id, chunks=len(chunks))
        
        return {
            "status": "success",
            "task_id": task_id,
            "chunks_count": len(chunks)
        }
        
    except Exception as e:
        logger.error("ingestion_failed", task_id=task_id, error=str(e))
        return {
            "status": "error",
            "task_id": task_id,
            "error": str(e)
        }
