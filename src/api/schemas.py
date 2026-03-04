from pydantic import BaseModel
from typing import Optional, List

# Ingestion Schemas
class IngestResponse(BaseModel):
    status: str
    task_id: str
    chunks_count: int
    error: Optional[str] = None

# Chat Schemas
class QueryRequest(BaseModel):
    query: str

class SourceInfo(BaseModel):
    file: str
    page: int

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
