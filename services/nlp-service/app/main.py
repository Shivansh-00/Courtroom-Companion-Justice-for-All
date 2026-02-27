from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="nlp-service")

class SimplifyRequest(BaseModel):
    text: str
    language: str = "en"

@app.get("/health")
def health():
    return {"status": "ok", "service": "nlp-service"}

@app.post("/simplify")
def simplify(payload: SimplifyRequest):
    plain = payload.text.replace("hereinafter", "from now on").replace("shall", "must")
    return {
        "summary": plain[:220],
        "plainLanguageSections": [{"title": "Simple explanation", "text": plain}],
        "voiceExplainerText": plain,
    }
