from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from config import DATABASE_URL

Base = declarative_base()

# Создание подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


new_session = async_sessionmaker(engine, expire_on_commit=False)
