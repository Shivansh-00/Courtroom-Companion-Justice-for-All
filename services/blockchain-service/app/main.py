from fastapi import FastAPI
from pydantic import BaseModel
import hashlib

app = FastAPI(title="blockchain-service")

class NotarizeRequest(BaseModel):
    documentId: str
    text: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "blockchain-service"}

@app.post("/notarize")
def notarize(payload: NotarizeRequest):
    digest = hashlib.sha256(payload.text.encode()).hexdigest()
    tx_hash = f"0x{digest[:64]}"
    return {
        "status": "CONFIRMED",
        "network": "polygon-amoy",
        "txHash": tx_hash,
        "contractAddress": "0x1234567890abcdef1234567890abcdef12345678"
    }
