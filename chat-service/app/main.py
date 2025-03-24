from fastapi import FastAPI
from routes import router
from database import create_tables

app = FastAPI(title="Auth Service")

app.include_router(router, prefix="/chat-service", tags=["Auth"])

@app.on_event("startup")
async def startup():
    await create_tables()
