import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.db_models import Document, DocumentChunk
from app.models.schemas import DocumentUploadResponse
from app.services.embeddings import generate_embeddings
from app.services.document_processor import (
    DocumentProcessingError,
    chunk_text,
    clean_text,
    extract_text_from_pdf,
    extract_text_from_txt,
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{extension}'. Allowed: {settings.allowed_extensions}",
        )

    raw_bytes = await file.read()
    size_mb = len(raw_bytes) / (1024 * 1024)
    if size_mb > settings.upload_max_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.upload_max_size_mb}MB limit.",
        )

    try:
        raw_text = extract_text_from_pdf(raw_bytes) if extension == "pdf" else extract_text_from_txt(raw_bytes)
    except DocumentProcessingError as exc:
        logger.warning("Extraction failed for %s: %s", file.filename, exc)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text found in this document.",
        )

    chunks = chunk_text(cleaned)

    document = Document(filename=file.filename, file_type=extension)
    db.add(document)
    await db.flush()  # assigns document.id without ending the transaction

    embeddings = await generate_embeddings(chunks)

    for index, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_content,
                embedding=embedding,
            )
        )

    await db.commit()
    await db.refresh(document)

    logger.info("Ingested '%s' into %d chunks", file.filename, len(chunks))

    return DocumentUploadResponse(
        id=document.id, filename=document.filename, file_type=document.file_type, chunk_count=len(chunks)
    )