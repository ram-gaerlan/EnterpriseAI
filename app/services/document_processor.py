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


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
    """Splits text into overlapping chunks, preferring paragraph boundaries
    over cutting at an arbitrary character count."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = current[-chunk_overlap:] + "\n\n" + paragraph
        else:
            # A single paragraph longer than chunk_size — hard-split it as a fallback
            current = paragraph[:chunk_size]
            chunks.append(current)
            current = paragraph[chunk_size - chunk_overlap:]

    if current:
        chunks.append(current)

    return chunks