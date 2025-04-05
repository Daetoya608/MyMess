from fastapi import FastAPI
from routes import router
from database import create_tables
import asyncio
from connection_manager import global_connection_manager

app = FastAPI(title="Auth Service")

app.include_router(router, prefix="/chat-service", tags=["Auth"])

@app.on_event("startup")
async def startup():
    await create_tables()
    asyncio.create_task(global_connection_manager.start_task())
    asyncio.create_task(global_connection_manager.delete_disconnected())


