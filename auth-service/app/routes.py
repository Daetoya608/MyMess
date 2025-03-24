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
    new_user_id: int = await add_user(username=user.username,
                                      email=user.email,
                                      password_hash=hash_password(user.password))
    if new_user_id <= 0:
        raise HTTPException(
            status_code=500,
            detail="something went wrong. Try again later"
        )
    response = await create_user_in_user_service(
        user.username, user.nickname, user.email
    )
    # !!!!!!!!!!!!!!! ДОБАВИТЬ  ПРОВЕРКУ СОВПАДЕНИЯ ID

    if not (200 <= response.status_code < 300):
        status = await delete_user_by_username(user.username)
        return JSONResponse(status_code=500, content={"status": status})


    token = create_jwt({"sub": user.username})

    return JSONResponse(content={"access_token": token, "token_type": "bearer"},
                        status_code=200)


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    try_find_user = await get_user_by_username(user.username)
    if not try_find_user:
        raise HTTPException(status_code=400, detail="1Not correct username or password")
    if not check_hash_and_password(user.password, try_find_user.password_hash):
        raise HTTPException(status_code=400, detail=f"Not correct username or password {try_find_user.password_hash} and {hash(user.password)}")

    token = create_jwt({"sub": user.username})
    return JSONResponse(content={"access_token": token, "token_type": "bearer"},
                        status_code=200)


