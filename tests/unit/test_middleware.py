import json


class TestRequestIDMiddleware:
    def test_request_gets_request_id_header(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.middleware.logging import RequestIDMiddleware

        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/health")
        def health():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        import uuid
        uid = response.headers["x-request-id"]
        uuid.UUID(uid)

    def test_existing_request_id_preserved(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.middleware.logging import RequestIDMiddleware

        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/health")
        def health():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/health", headers={"x-request-id": "my-custom-id"})
        assert response.headers["x-request-id"] == "my-custom-id"