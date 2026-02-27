from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="matchmaking-service")

class MatchRequest(BaseModel):
    documentId: str
    location: str
    needs: list[str]

@app.get("/health")
def health():
    return {"status": "ok", "service": "matchmaking-service"}

@app.post("/recommendations")
def recommendations(payload: MatchRequest):
    return {
        "matches": [
            {
                "providerId": "ngo_11",
                "name": "Justice Bridge Foundation",
                "score": 0.91,
                "availability": "<24h",
                "languages": ["en", "sw"]
            }
        ]
    }
