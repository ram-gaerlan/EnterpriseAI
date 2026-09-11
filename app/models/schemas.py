from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    chunk_count: int

class QuestionRequest(BaseModel):
    question: str


class SourceInfo(BaseModel):
    document: str
    chunk: int
    similarity: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]