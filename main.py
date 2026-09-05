from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


class SignUpRequest(BaseModel):
    email: str
    password: str


class LogInRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/signup", status_code=201)
def auth_signup(user: SignUpRequest):
    if user.email is None or user.password is None:
        raise HTTPException(
            status_code=400,
            detail="Bad Request"
        )

    response = supabase.auth.sign_up({
        "email": user.email,
        "password": user.password
    })

    return response


@app.post("/auth/login", status_code=200)
def auth_login(user: LogInRequest):
    if user.email is None or user.password is None:
        raise HTTPException(
            status_code=400,
            detail="Empty Fields"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid login credentials"}
        )

    return response

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


@app.get("/protected/profile")
def protected_profile(authorization: str | None = Header(default=None)):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail={"error": "Access token required"}
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={"error": "Access token required"}
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Access token required"}
        )

    return {"message": "Token presented"}