from fastapi import APIRouter, HTTPException
from models import User, get_user_by_username, add_user
from schemas import UserCreate
from user import hash_password, create_jwt, decode_jwt
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("/users/{token}")
async def register(token: str):
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=400,
            detail="username already exists"
        )

    user = await get_user_by_username(payload["username"])
    if user:
        raise HTTPException(
            status_code=400,
            detail="username already exists"
        )

    new_user_id: int = await add_user(username=payload["username"],
                                      nickname=payload["nickname"],
                                      email=payload["email"])

    if new_user_id <= 0:
        raise HTTPException(
            status_code=500,
            detail="something went wrong. Try again later"
        )

    token = create_jwt(
        {
            "sub": payload["username"],
            "username": payload["username"],
            "nickname": payload["nickname"],
            "email": payload["email"],
            "info_about_yourself": "",
         }
    )

    return JSONResponse(content={"access_token": token, "token_type": "bearer"},
                        status_code=201)


