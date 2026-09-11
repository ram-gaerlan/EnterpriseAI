import logging

from google import genai

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

client = genai.Client(api_key=settings.gemini_api_key)

GENERATION_MODEL = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant that answers questions using ONLY the "
    "provided context from uploaded company documents. "
    "If the answer cannot be found in the provided context, say that the "
    "information could not be found in the uploaded documents. "
    "Do not invent an answer or use outside knowledge."
)


def build_context(chunks_with_sources: list[tuple[str, str, int]]) -> str:
    """Formats retrieved chunks into labeled context blocks.

    Each item is (content, filename, chunk_index).
    """
    blocks = [
        f"[Source: {filename}, chunk {chunk_index}]\n{content}"
        for content, filename, chunk_index in chunks_with_sources
    ]
    return "\n\n---\n\n".join(blocks)


async def generate_answer(question: str, context: str) -> str:
    prompt = (
        f"Context from uploaded documents:\n\n{context}\n\n"
        f"---\n\nQuestion: {question}\n\nAnswer:"
    )

    response = await client.aio.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION
        ),
    )

    return response.text