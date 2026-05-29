import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_submit_request_success(client):
    response = client.post(
        "/api/submit",
        json={
            "employee_id": "EMP-001",
            "employee_name": "John Doe",
            "employee_email": "john@company.com",
            "department": "Engineering",
            "message": "My printer is broken",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["status"] == "acknowledged"
    assert data["category"] == "Unknown"
    assert "created_at" in data


def test_submit_request_validation_error(client):
    response = client.post(
        "/api/submit",
        json={
            "employee_id": "EMP-001",
            "employee_email": "not-an-email",
            "department": "Engineering",
            "message": "My printer is broken",
        },
    )
    assert response.status_code == 422


def test_response_includes_request_id_header(client):
    response = client.post(
        "/api/submit",
        json={
            "employee_id": "EMP-001",
            "employee_name": "John Doe",
            "employee_email": "john@company.com",
            "department": "Engineering",
            "message": "My printer is broken",
        },
    )
    assert "x-request-id" in response.headers