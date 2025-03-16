from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from database import Base, new_session

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)


async def add_user(username: str, email: str, password_hash: str):
    async with new_session() as session:
        new_user = User(username=username, email=email, password_hash=password_hash)
        session.add(new_user)
        try:
            await session.commit()
            print(f"User {new_user} was added")
            return 1
        except IntegrityError:
            await session.rollback()
            print("Error: user is in base")
            return 0

async def get_user_by_id(user_id: int) -> Optional[str]:
    async with new_session() as session:
        user = await session.get(User, user_id)
        return user


async def get_user_by_username(username: str) -> Optional[str]:
    async with new_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

