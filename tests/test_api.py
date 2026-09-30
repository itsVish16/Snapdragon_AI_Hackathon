from fastapi.testclient import TestClient
from snapflow.web.app import app

client = TestClient(app)


def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "provider" in data
    assert "target_soc" in data


def test_api_refine():
    payload = {
        "text": "umm so basically we need to test this api like right now",
        "style": "clean_verbatim",
    }
    response = client.post("/api/refine", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "refined" in data
    assert "umm" not in data["refined"].lower()


def test_api_inject():
    payload = {"text": "Test injection string"}
    response = client.post("/api/inject", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
