from fastapi import FastAPI

app = FastAPI(
    title="OfficeGenie API",
    description="AI-powered first-line triage system for employee support requests.",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
