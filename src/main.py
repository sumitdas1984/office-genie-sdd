from fastapi import FastAPI

app = FastAPI(
    title="OfficeGenie",
    description="AI-powered first-line triage system for employee support requests.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}