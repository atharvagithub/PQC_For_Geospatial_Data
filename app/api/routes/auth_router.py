from fastapi import APIRouter, Response, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.infrastructure.session_manager import create_session_cookie, SESSIONS

router = APIRouter(prefix="/api/blockchain", tags=["Blockchain"])

class LoginRequest(BaseModel):
    private_key: str

@router.post("/login")
def login(req: LoginRequest, response: Response):
    # Optionally validate private key or derive address
    create_session_cookie(response, req.private_key)
    return {"message": "Login successful"}

@router.post("/logout")
def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token in SESSIONS:
        del SESSIONS[session_token]
    response.delete_cookie("session_token")
    return {"message": "Logged out"}

@router.post("/check_session")
async def check_session(request: Request):
    session_token = request.cookies.get("session_token")
    print(f"[DEBUG] Received session token: {session_token}")
    if session_token and session_token in SESSIONS:
        return JSONResponse(content={"valid": True})
    return JSONResponse(content={"valid": False})