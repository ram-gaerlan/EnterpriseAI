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

class UserRegister(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"