import httpx
from fastapi import HTTPException
from auth import create_jwt

host = "127.0.0.1"

async def create_user_in_user_service(username: str, nickname: str, email: str):
    token = create_jwt(
        {
            "username": username,
            "nickname": nickname,
            "email": email,
        }
    )
    user_service_url = f"http://{host}:8002/user-service/users/{token}"
    print(f"create_user_in_user_service - mid")
    async with httpx.AsyncClient() as client:
        response = await client.post(user_service_url)
        return response
