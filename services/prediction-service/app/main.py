from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="prediction-service")

class PredictRequest(BaseModel):
    text: str
    jurisdiction: str = "global"

@app.get("/health")
def health():
    return {"status": "ok", "service": "prediction-service"}

@app.post("/predict")
def predict(payload: PredictRequest):
    score = 0.74 if "appeal" in payload.text.lower() else 0.62
    return {
        "outcome": "LikelySettlement" if score > 0.7 else "FurtherReviewNeeded",
        "score": score,
        "confidence": 0.82,
        "biasFlags": ["none_detected"],
        "riskHeatmap": [
            {"region": "North", "risk": 0.41},
            {"region": "Central", "risk": 0.68},
            {"region": "South", "risk": 0.55}
        ]
    }
