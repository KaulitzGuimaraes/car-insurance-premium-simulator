from fastapi.testclient import TestClient

from app.main import create_app


def test_health():
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_includes_health_and_quote():
    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/quotes" in paths


def test_quote_calculation():
    payload = {
        "broker_fee": 50.0,
        "deductible_percentage": 0.10,
        "make": "Toyota",
        "model": "Corolla",
        "value": 100000.0,
        "year": 2016,
    }
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/quotes", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["calculated_premium"] > 0
    assert body["car"] == {
        "make": "Toyota",
        "model": "Corolla",
        "value": 100000.0,
        "year": 2016,
    }
    assert body["deductible_value"] == 10000.0
    assert body["policy_limit"] == 90000.0
