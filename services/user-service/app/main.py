from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import jwt
import os

app = FastAPI(title="user-service")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}

@app.post("/auth/login")
def login(payload: LoginRequest):
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    role = "citizen" if not payload.email.endswith("@admin.justice") else "court_admin"
    token = jwt.encode({"sub": payload.email, "role": role}, JWT_SECRET, algorithm="HS256")
    return {
        "accessToken": token,
        "refreshToken": f"refresh-{payload.email}",
        "expiresIn": 900,
        "role": role,
        "mfaRequired": role != "citizen"
    }
