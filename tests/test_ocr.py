from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_no_file():
    resp = client.post("/ocr")
    assert resp.status_code == 422

def test_invalid_type():
    resp = client.post("/ocr", files={"file": ("a.txt", b"hello", "text/plain")})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "file_missing"
