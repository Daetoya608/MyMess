from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]
