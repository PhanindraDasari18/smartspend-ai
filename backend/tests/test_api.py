from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
def test_health_is_public():
    assert client.get("/health").json() == {"status": "ok"}

def test_protected_route_requires_auth():
    assert client.post("/api/v1/analyze", json={"transactions": []}).status_code == 401

def test_invalid_categorize_payload():
    assert client.post("/api/v1/categorize", json={}).status_code == 401
