from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    chunk_count: int