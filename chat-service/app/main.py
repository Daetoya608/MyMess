from fastapi import FastAPI
# from routes import router
from database import create_tables
import asyncio
from connection_manager import global_connection_manager
from sockets import router
from chat import create_jwt

app = FastAPI(title="Chat Service")

app.include_router(router)

print(create_jwt(
    payload={
        "id": 1,
        "username": "forexample1"
    }
))

print("--------------")

print(create_jwt(
    payload={
        "id": 2,
        "username": "forexample2"
    }
))

@app.on_event("startup")
async def startup():
    await create_tables()
    # asyncio.create_task(global_connection_manager.start_task())
    # asyncio.create_task(global_connection_manager.delete_disconnected())


