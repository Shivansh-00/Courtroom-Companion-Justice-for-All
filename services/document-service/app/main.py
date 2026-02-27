from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="document-service")

DOCS: dict[str, dict] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "document-service"}

@app.post("/documents")
async def create_document(file: UploadFile = File(...), language: str = Form("en"), jurisdiction: str = Form("global"), privacyMode: bool = Form(False)):
    document_id = f"doc_{uuid4().hex[:12]}"
    pipeline_id = f"pipe_{uuid4().hex[:12]}"
    DOCS[document_id] = {
        "documentId": document_id,
        "status": "QUEUED",
        "language": language,
        "jurisdiction": jurisdiction,
        "privacyMode": privacyMode,
        "filename": file.filename,
        "progress": 0,
        "pipelineId": pipeline_id,
    }
    return {"documentId": document_id, "status": "QUEUED", "pipelineId": pipeline_id, "estimatedSeconds": 35}

@app.get("/documents/{document_id}")
def get_document(document_id: str):
    return DOCS.get(document_id, {"documentId": document_id, "status": "NOT_FOUND", "progress": 0})
