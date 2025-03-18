from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from database import Base, new_session

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    nickname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    info_about_yourself = Column(String, default="", nullable=False)


async def add_user(username: str, nickname: str, email: str,
                   info_about_yourself: str = ""):
    async with new_session() as session:
        new_user = User(username=username,
                        nickname=nickname,
                        email=email,
                        info_about_yourself=info_about_yourself)
        session.add(new_user)
        try:
            await session.commit()
            print(f"User {new_user} was added")
            return new_user.id
        except IntegrityError:
            await session.rollback()
            print("Error: user is in base")
            return 0


async def get_user_by_id(user_id: int):
    async with new_session() as session:
        user = await session.get(User, user_id)
        return user


async def get_user_by_username(username: str):
    async with new_session() as session:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


async def delete_user_by_id(id: int):
    finded_user = await get_user_by_id(id)
    if finded_user is None:
        print("User is not in base")
        return 0
    async with new_session() as session:
        await session.delete(finded_user)
        try:
            await session.commit()
            print(f"User {finded_user} was deleted")
            return 1
        except IntegrityError:
            await session.rollback()
            print("Error: cant delete user")
            return 0


async def delete_user_by_username(username: str):
    finded_user = await get_user_by_username(username)
    if finded_user is None:
        print("User is not in base")
        return 0
    return await delete_user_by_id(finded_user.id)
