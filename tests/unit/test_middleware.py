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


def test_log_line_is_valid_json(capfd):
    import logging
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

    captured = capfd.readouterr()
    lines = [line for line in captured.out.strip().split("\n") if line.strip()]
    assert len(lines) >= 2
    for line in lines:
        parsed = json.loads(line)
        assert "request_id" in parsed
        assert "event" in parsed