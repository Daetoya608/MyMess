from fastapi import APIRouter, HTTPException, Query
from models import User, get_user_by_username, add_user, get_user_by_id
from schemas import UserCreate, UserInfoRequest
from user import hash_password, create_jwt, decode_jwt
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("/users/{token}")
async def register(token: str):
    print(f"\nregister - begin")
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

    new_user = await add_user(username=payload["username"],
                                      nickname=payload["nickname"],
                                      email=payload["email"])

    if new_user is None:
        raise HTTPException(
            status_code=500,
            detail="something went wrong. Try again later"
        )
    print(f"register - id={new_user.id}")
    token = create_jwt(
        {
            "sub": payload["username"],
            "user_id": new_user.id,
            "username": payload["username"],
            "nickname": payload["nickname"],
            "email": payload["email"],
            "info_about_yourself": "",
         }
    )

    return JSONResponse(content={"user_id": new_user.id, "access_token": token, "token_type": "bearer",
                                 "username": new_user.username, "email": new_user.email,
                                 "nickname": new_user.nickname},
                        status_code=201)


@router.get("/info")
async def get_info(users_ids: str = Query(...)):
    users_ids_list = [int(user_id) for user_id in users_ids.split(",")]
    print(f"get_info - begin")
    users_data = []
    for user_id in users_ids_list:
        user = await get_user_by_id(user_id)
        if user is None:
            continue
        users_data.append({
            "user_id": user.id,
            "username": user.username,
            "nickname": user.nickname,
        })
    print(f"get_info - users_data = {users_data}")
    return JSONResponse(content={"users_data": users_data}, status_code=200)


@router.get("/user_id/{username}")
async def get_user_id(username: str):
    try_find_user = await get_user_by_username(username)
    print(try_find_user)
    if not try_find_user:
        raise HTTPException(status_code=400, detail="User does not exist")

    return JSONResponse(status_code=200, content={
        "user_id": try_find_user.id,
        "username": try_find_user.username,
        "nickname": try_find_user.nickname,
        "user_info": try_find_user.info_about_yourself,
    })


# @router.get("/aboba")
# async def get_aboba(numbers: str = Query(...)):
#     numbers_list = [int(num) for num in numbers.split(",")]
#     print(numbers_list)
#     return JSONResponse(content={}, status_code=200)