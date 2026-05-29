import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_has_submit_endpoint(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/api/submit" in schema["paths"]
    assert "post" in schema["paths"]["/api/submit"]


def test_submit_request_schema_in_openapi(client):
    response = client.get("/openapi.json")
    schema = response.json()
    submit_schema = schema["paths"]["/api/submit"]["post"]
    assert "422" in submit_schema["responses"]


def test_request_id_in_openapi_security(client):
    response = client.get("/openapi.json")
    schema = response.json()
    submit_params = schema["paths"]["/api/submit"]["post"].get("parameters", [])
    header_names = [p["name"] for p in submit_params]