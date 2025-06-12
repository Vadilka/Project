import os
import tempfile
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_upload_pdf():
    # Создаём временный PDF-файл
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_pdf.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF')
    temp_pdf.close()
    with open(temp_pdf.name, "rb") as f:
        response = client.post("/upload", files={"file": (os.path.basename(temp_pdf.name), f, "application/pdf")})
    os.unlink(temp_pdf.name)
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert data["filename"].endswith(".pdf")
    assert "status" in data and data["status"] == "added to vector store"

def test_chat():
    # Простой тест запроса к чату
    response = client.post("/chat", json={"message": "Jakie są przedmioty na 1 semestrze?", "history": []})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data 