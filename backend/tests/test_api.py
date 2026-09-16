import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_quote_file_txt_success():
    sample_text = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    files = {"file": ("test_doc.txt", io.BytesIO(sample_text), "text/plain")}

    response = client.post("/api/v1/quote/file", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_doc.txt"
    assert data["source_type"] == "text"
    assert data["used_ocr"] is False
    assert data["sworn_page_count"] == 1
    assert data["raw_character_count"] == len(sample_text)


def test_quote_rejects_empty_file():
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}

    response = client.post("/api/v1/quote/file", files=files)

    assert response.status_code == 400
    assert "Uploaded file is empty." in response.json()["detail"]


def test_quote_rejects_unsupported_file_extension():
    files = {
        "file": ("test.exe", io.BytesIO(b"dummy data"), "application/octet-stream")
    }

    response = client.post("/api/v1/quote/file", files=files)

    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]
