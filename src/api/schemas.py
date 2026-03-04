from pydantic import BaseModel
from typing import Optional

class IngestResponse(BaseModel):
    status: str
    task_id: str
    chunks_count: int
    error: Optional[str] = None
