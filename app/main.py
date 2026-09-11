import logging

from fastapi import FastAPI

from app.config import get_settings

from app.routers import documents

from app.routers import documents, questions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()  # Validates env vars are present at startup

app = FastAPI(
    title="RAG Document Intelligence — Phase 1",
    description="A minimal Retrieval-Augmented Generation system for company documents.",
    version="0.1.0",
)

app.include_router(documents.router)
app.include_router(questions.router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness check — confirms the API process is up and config loaded successfully."""
    return {"status": "ok"}