import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import AnswerResponse, QuestionRequest, SourceInfo
from app.services.embeddings import generate_query_embedding
from app.services.rag import build_context, generate_answer
from app.services.retrieval import find_similar_chunks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
) -> AnswerResponse:
    query_embedding = await generate_query_embedding(request.question)
    results = await find_similar_chunks(db, query_embedding, top_k=5)

    context = build_context(
        [(chunk.content, document.filename, chunk.chunk_index) for chunk, document, _ in results]
    )

    answer = await generate_answer(request.question, context)

    sources = [
        SourceInfo(document=document.filename, chunk=chunk.chunk_index, similarity=round(similarity, 3))
        for chunk, document, similarity in results
    ]

    logger.info("Answered question with %d source chunks", len(sources))

    return AnswerResponse(answer=answer, sources=sources)