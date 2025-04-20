import httpx
import asyncio

request_data = [("users_ids", 15), ("users_ids", 14)]

async def send_request():
    async with httpx.AsyncClient() as client:
        print(f"get_users_info - client.begin")
        response = await client.get("http://127.0.0.1:8002/user-service/aboba",
                                    params={"numbers": "15,14"})
        print(response.status_code)
        print(response.json())


asyncio.run(send_request())
