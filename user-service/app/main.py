from fastapi import FastAPI
from routes import router
from database import create_tables

app = FastAPI(title="User Service")

app.include_router(router, prefix="/user-service", tags=["User"])

@app.on_event("startup")
async def startup():
    await create_tables()
