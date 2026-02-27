from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="notification-service")

class ReminderRequest(BaseModel):
    documentId: str
    hearingDate: str
    channels: list[str]
    timezone: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}

@app.post("/reminders")
def create_reminder(payload: ReminderRequest):
    return {
        "status": "scheduled",
        "documentId": payload.documentId,
        "channels": payload.channels,
        "nextRunAt": payload.hearingDate
    }
