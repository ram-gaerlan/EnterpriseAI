import pytest

from app.services.document_processor import chunk_text, clean_text


def test_clean_text_collapses_whitespace():
    messy = "Hello    world\n\n\n\nGoodbye"
    assert clean_text(messy) == "Hello world\n\nGoodbye"


def test_clean_text_strips_null_bytes():
    assert clean_text("a\x00b") == "ab"


def test_chunk_text_respects_paragraph_boundaries():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=50)
    # Short text well under chunk_size should stay as a single chunk
    assert len(chunks) == 1
    assert "Paragraph one." in chunks[0]


def test_chunk_text_splits_long_content():
    long_paragraph = "word " * 500  # ~2500 characters, exceeds default chunk_size
    chunks = chunk_text(long_paragraph, chunk_size=1000, chunk_overlap=100)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 1000 + 100  # allow for overlap prefix


def test_chunk_text_empty_input_returns_empty_list():
    assert chunk_text("") == []