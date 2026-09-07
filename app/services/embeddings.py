import logging

from google import genai
from google.genai import types

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

client = genai.Client(api_key=settings.gemini_api_key)

EMBEDDING_MODEL = "gemini-embedding-001"
OUTPUT_DIMENSIONS = 768


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates one embedding per input string, in the same order they were given."""
    if not texts:
        return []

    response = await client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=OUTPUT_DIMENSIONS,
            task_type="RETRIEVAL_DOCUMENT",
        ),
    )

    return [embedding.values for embedding in response.embeddings]