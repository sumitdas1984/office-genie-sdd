from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.api.exceptions import validation_exception_handler
from src.api.routes import router as api_router
from src.middleware.logging import RequestIDMiddleware

app = FastAPI(
    title="OfficeGenie",
    description="AI-powered first-line triage system for employee support requests.",
    version="0.1.0",
)

app.add_middleware(RequestIDMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}