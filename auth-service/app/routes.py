from fastapi import APIRouter, HTTPException
from schemas import UserCreate, UserLogin, Token
from models import User, get_user_by_username, add_user, delete_user_by_username
from auth import create_jwt, hash_password, check_hash_and_password
from fastapi.responses import JSONResponse
from serviceRequests import create_user_in_user_service


router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    try_find_user = await get_user_by_username(user.username)
    if try_find_user:
        raise HTTPException(
            status_code=400,
            detail="username already exists"
        )
    response = await create_user_in_user_service(
        user.username, user.nickname, user.email
    )

    if not (200 <= response.status_code < 300):
        return JSONResponse(status_code=500, content={"status": False, "description": "ошибка создания"})
    new_user_from_user_service = response.json()
    new_user: User = await add_user(user_id=new_user_from_user_service["user_id"],
                                    username=new_user_from_user_service["username"],
                                    email=new_user_from_user_service["email"],
                                    password_hash=hash_password(user.password))
    if new_user is None:
        raise HTTPException(
            status_code=500,
            detail="something went wrong. Try again later"
        )

    token = create_jwt({
        "sub": new_user.username,
        "username": new_user.username,
        "id": new_user.id,
        "email": new_user.email
    })

    return JSONResponse(content={"token": token, "token_type": "bearer",
                                 "user_id": new_user.user_id, "username": new_user.username,
                                 "email": new_user.email, "nickname": new_user_from_user_service["nickname"]},
                        status_code=200)


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    try_find_user = await get_user_by_username(user.username)
    if not try_find_user:
        raise HTTPException(status_code=400, detail="1Not correct username or password")
    if not check_hash_and_password(user.password, try_find_user.password_hash):
        raise HTTPException(status_code=400, detail=f"Not correct username or password {try_find_user.password_hash} and {hash(user.password)}")

    token = create_jwt({
        "sub": try_find_user.username,
        "username": try_find_user.username,
        "id": try_find_user.id,
        "email": try_find_user.email
    })
    return JSONResponse(content={"access_token": token, "token_type": "bearer", "id": try_find_user.id},
                        status_code=200)


