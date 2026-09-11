import logging
import re

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Raised when a file's text cannot be extracted."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            pages = [page.get_text() for page in pdf]
    except Exception as exc:  # PyMuPDF raises various internal exceptions on corrupt files
        raise DocumentProcessingError(f"Failed to parse PDF: {exc}") from exc
    return "\n\n".join(pages)


def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Some files are saved in a legacy encoding — fall back rather than fail outright
        return file_bytes.decode("latin-1")


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")        # PDFs occasionally embed stray null bytes
    text = re.sub(r"[ \t]+", " ", text)    # collapse repeated spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text) # collapse 3+ blank lines down to one
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> list[str]:
    """Split text into overlapping chunks while preferring paragraph boundaries."""

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:

        # Handle paragraphs larger than chunk_size separately.
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""

            start = 0

            while start < len(paragraph):
                end = start + chunk_size
                chunk = paragraph[start:end]
                chunks.append(chunk)

                if end >= len(paragraph):
                    break

                start = end - chunk_overlap

            continue

        # Try adding the paragraph to the current chunk.
        candidate = f"{current}\n\n{paragraph}" if current else paragraph

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            # Save the current chunk.
            if current:
                chunks.append(current)

            # Start a new chunk with the paragraph.
            current = paragraph

    if current:
        chunks.append(current)

    return chunks