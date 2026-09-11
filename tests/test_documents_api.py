from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_upload_txt_document(client):
    fake_embeddings = [[0.1] * 768]

    with patch(
        "app.routers.documents.generate_embeddings",
        new=AsyncMock(return_value=fake_embeddings),
    ):
        files = {"file": ("test.txt", b"This is a short test document.", "text/plain")}
        response = await client.post("/documents/upload", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "test.txt"
    assert body["chunk_count"] == 1


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_file_type(client):
    files = {"file": ("test.docx", b"fake content", "application/octet-stream")}
    response = await client.post("/documents/upload", files=files)

    assert response.status_code == 400