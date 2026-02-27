from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import os
import jwt
import asyncio
from collections import defaultdict, deque
from time import time

app = FastAPI(title="api-gateway")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://document-service:8000")
NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL", "http://nlp-service:8000")
PREDICTION_SERVICE_URL = os.getenv("PREDICTION_SERVICE_URL", "http://prediction-service:8000")
BLOCKCHAIN_SERVICE_URL = os.getenv("BLOCKCHAIN_SERVICE_URL", "http://blockchain-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")
MATCHMAKING_SERVICE_URL = os.getenv("MATCHMAKING_SERVICE_URL", "http://matchmaking-service:8000")

rate_store: dict[str, deque] = defaultdict(deque)
connections: dict[str, list[WebSocket]] = defaultdict(list)


def validate_token(auth_header: str | None):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth_header.split(" ", 1)[1]
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def enforce_rate_limit(subject: str, limit: int = 120, window_sec: int = 60):
    now = time()
    bucket = rate_store[subject]
    while bucket and bucket[0] <= now - window_sec:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    bucket.append(now)


@app.exception_handler(HTTPException)
async def handled_http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "error": {
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "retryable": exc.status_code in [408, 409, 429, 500, 502, 503, 504],
            "correlationId": request.headers.get("x-correlation-id", "auto-correlation-id")
        }
    })


@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway"}


@app.post("/v1/auth/login")
async def login(payload: dict):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{USER_SERVICE_URL}/auth/login", json=payload)
    return response.json()


@app.post("/v1/documents")
async def create_document(
    authorization: str | None = Header(None),
    file: UploadFile = File(...),
    language: str = Form("en"),
    jurisdiction: str = Form("global"),
    privacyMode: bool = Form(False),
):
    claims = validate_token(authorization)
    enforce_rate_limit(claims["sub"])

    async with httpx.AsyncClient(timeout=30) as client:
        files = {"file": (file.filename, await file.read(), file.content_type or "application/octet-stream")}
        data = {
            "language": language,
            "jurisdiction": jurisdiction,
            "privacyMode": str(privacyMode).lower(),
        }
        response = await client.post(f"{DOCUMENT_SERVICE_URL}/documents", files=files, data=data)
        result = response.json()

    asyncio.create_task(simulate_pipeline(result["documentId"], result["pipelineId"]))
    return result


@app.get("/v1/documents/{document_id}")
async def get_document(document_id: str, authorization: str | None = Header(None)):
    claims = validate_token(authorization)
    enforce_rate_limit(claims["sub"])
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"{DOCUMENT_SERVICE_URL}/documents/{document_id}")
    return response.json()


@app.get("/v1/documents/{document_id}/result")
async def get_result(document_id: str, authorization: str | None = Header(None)):
    claims = validate_token(authorization)
    enforce_rate_limit(claims["sub"])
    text = f"Document {document_id} shall be reviewed hereinafter in accordance with statute."

    async with httpx.AsyncClient(timeout=20) as client:
        simplify = await client.post(f"{NLP_SERVICE_URL}/simplify", json={"text": text, "language": "en"})
        predict = await client.post(f"{PREDICTION_SERVICE_URL}/predict", json={"text": text, "jurisdiction": "global"})
        chain = await client.post(f"{BLOCKCHAIN_SERVICE_URL}/notarize", json={"documentId": document_id, "text": text})

    return {
        **simplify.json(),
        "prediction": predict.json(),
        "blockchain": {
            **chain.json(),
            "verificationUrl": f"https://amoy.polygonscan.com/tx/{chain.json()['txHash']}"
        },
    }


@app.post("/v1/reminders")
async def reminders(payload: dict, authorization: str | None = Header(None)):
    claims = validate_token(authorization)
    enforce_rate_limit(claims["sub"])
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{NOTIFICATION_SERVICE_URL}/reminders", json=payload)
    return response.json()


@app.post("/v1/matchmaking/recommendations")
async def recommendations(payload: dict, authorization: str | None = Header(None)):
    claims = validate_token(authorization)
    enforce_rate_limit(claims["sub"])
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{MATCHMAKING_SERVICE_URL}/recommendations", json=payload)
    return response.json()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return

    subject = claims.get("sub", "unknown")
    await websocket.accept()
    connections[subject].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections[subject].remove(websocket)


async def simulate_pipeline(document_id: str, pipeline_id: str):
    stages = [
        ("OCR", 20, "Extracting text from document"),
        ("SIMPLIFICATION", 55, "Generating plain-language explanation"),
        ("PREDICTION", 80, "Calculating case outcome probabilities"),
        ("BLOCKCHAIN", 100, "Notarizing hash on Polygon Amoy"),
    ]
    for stage, progress, message in stages:
        await asyncio.sleep(1)
        event = {
            "event": "pipeline.progress",
            "payload": {
                "documentId": document_id,
                "correlationId": pipeline_id,
                "stage": stage,
                "progress": progress,
                "message": message,
            },
        }
        for sockets in connections.values():
            for ws in sockets:
                await ws.send_json(event)
