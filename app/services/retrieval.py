import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Document, DocumentChunk

logger = logging.getLogger(__name__)


async def find_similar_chunks(
    db: AsyncSession,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[tuple[DocumentChunk, Document, float]]:
    """Returns the top_k chunks most similar to query_embedding, each paired
    with its parent Document and a similarity score (1.0 = identical, 0 = unrelated)."""
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(DocumentChunk, Document, distance.label("distance"))
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    result = await db.execute(stmt)

    return [
        (chunk, document, 1 - dist)  # convert distance -> similarity
        for chunk, document, dist in result.all()
    ]