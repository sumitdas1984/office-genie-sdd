def test_app_boots():
    from src.main import app
    assert app is not None


def test_health_check():
    from src.main import app
    from starlette.testclient import TestClient

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
