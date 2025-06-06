import os, uuid
from dotenv import load_dotenv
from fastapi import Response, Request, HTTPException
from itsdangerous import URLSafeSerializer

SESSIONS = {}

load_dotenv()

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")  # 🔐 Replace with env secret
serializer = URLSafeSerializer(SECRET_KEY)

def create_session_cookie(response: Response, private_key: str):
    #signed_data = serializer.dumps(private_key)
    session_token = str(uuid.uuid4())
    SESSIONS[session_token] = private_key
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # Set True in production
        max_age=36000,
        samesite="Lax"
    )

def get_private_key_from_cookie(request: Request) -> str:
    cookie = request.cookies.get("session_token")
    if not cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # No decoding needed – raw UUID lookup
    private_key = SESSIONS.get(cookie)
    if not private_key:
        raise HTTPException(status_code=403, detail="Invalid session token")
    
    return private_key

