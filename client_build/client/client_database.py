from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey, select, distinct, func
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from typing import Dict, List

from pathlib import Path
import appdirs

appname = "MyMess"
data_dir = Path(appdirs.user_data_dir(appname))
data_dir.mkdir(parents=True, exist_ok=True)  # auto-create dir
db_path = data_dir / "client.db"
print(f"DATABASE={db_path}")

# Для SQLite нужно использовать aiosqlite
# DATABASE_URL = "sqlite+aiosqlite:///./client.db"  # файл test.db в текущей директории
DATABASE_URL = f"sqlite+aiosqlite:///{db_path.as_posix()}"

Base = declarative_base()

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронная фабрика сессий
new_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Chat(Base):
    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, nullable=False, unique=True)
    chat_name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    messages = relationship("Message", back_populates="chat")
    connects = relationship("Connect", back_populates="chat")


class Connect(Base):
    __tablename__ = "Connect"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey("Chat.chat_id"), nullable=False)

    chat = relationship("Chat", back_populates="connects")


class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, nullable=False, unique=True)
    sender_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey("Chat.chat_id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    content_text = Column(Text, nullable=False)

    chat = relationship("Chat", back_populates="messages")

    def to_dict(self):
        data = {
            "id": self.id,
            "sender_id": self.sender_id,
            "chat_id": self.chat_id,
            "content_text": self.content_text,
        }
        return data


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(Text, unique=True, nullable=False)
    nickname = Column(Text, nullable=False)

    def to_dict(self):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "nickname": self.nickname,
        }
        return data


async def add_user(user_id: int, username: str, nickname: str):
    async with new_session() as session:
        new_user = User(user_id=user_id, username=username, nickname=nickname)
        session.add(new_user)
        try:
            await session.commit()
            # print(f"User {new_user.username} was added")
            return new_user
        except IntegrityError:
            await session.rollback()
            print(f"Error: cant add user {new_user.username}")
            return None


async def add_user_by_obj(user_info: Dict):
    result = await add_user(
        user_id=user_info["user_id"],
        username=user_info["username"],
        nickname=user_info["nickname"]
    )
    return result


async def add_chat(chat_name: str, chat_id: int) -> Chat | None:
    async with new_session() as session:
        new_chat = Chat(chat_name=chat_name, chat_id=chat_id)
        session.add(new_chat)
        try:
            await session.commit()
            # print(f"Chat {new_chat} was added")
            return new_chat
        except IntegrityError:
            await session.rollback()
            print(f"Error: cant add chat {new_chat}")
            return None


async def add_connect(user_id: int, chat_id: int):
    async with new_session() as session:
        new_connect = Connect(user_id=user_id, chat_id=chat_id)
        session.add(new_connect)
        try:
            await session.commit()
            # print(f"Connect {new_connect} was added")
            return new_connect
        except IntegrityError:
            await session.rollback()
            print(f"Error: cant add connect {new_connect}")
            return None


async def add_message(message_id: int, sender_id: int, chat_id: int, content_text: str):
    async with new_session() as session:
        new_message = Message(message_id=message_id, sender_id=sender_id, chat_id=chat_id, content_text=content_text)
        session.add(new_message)
        try:
            await session.commit()
            # print(f"\n!!!!\nMessage {new_message} was added\n!!!!\n")
            return new_message
        except IntegrityError:
            await session.rollback()
            print(f"\n???????? Error: cant add message {new_message}\n")
            return None


async def add_message_by_obj(data: dict) -> Message | None:
    try:
        new_message = await add_message(
            message_id=data["id"],
            sender_id=data["sender_id"],
            chat_id=data["chat_id"],
            content_text=data["content_text"]
        )
        return new_message
    except Exception as e:
        print(f"add_message_by_obj: {e}")
        return None

async def get_connects_by_user_id(user_id: int) -> list[Connect]:
    async with new_session() as session:
        result = await session.execute(
            select(Connect).where(Connect.user_id == user_id)
        )
        return list(result.scalars().all())


async def get_users_by_chat_id(chat_id: int) -> list:
    async with new_session() as session:
        result = await session.execute(
            select(Connect).where(Connect.chat_id == chat_id)
        )
        return list(result.scalars().all())


async def get_user_by_user_id(user_id: int):
    async with new_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def get_unique_user_ids():
    async with new_session() as session:
        result = await session.execute(
            select(distinct(Connect.user_id))
        )
        return result.scalars().all()


async def get_unique_chat_ids():
    async with new_session() as session:
        result = await session.execute(
            select(distinct(Connect.chat_id))
        )
        return result.scalars().all()


async def get_messages_by_chat_id(chat_id: int):
    async with new_session() as session:
        result = await session.execute(
            select(Message).where(Message.chat_id == chat_id)
        )
        return list(result.scalars().all())


async def get_unique_chats():
    async with new_session() as session:
        result = await session.execute(select(Chat))
        return list(result.scalars().all())


async def get_chat_by_chat_id(chat_id: int):
    async with new_session() as session:
        result = await session.execute(
            select(Chat).where(Chat.chat_id == chat_id)
        )
        return result.scalar_one_or_none()


async def get_chats_by_user_id(user_id: int) -> List[Chat]:
    connects_list = await get_connects_by_user_id(user_id)
    result = []
    for connect in connects_list:
        chat = await get_chat_by_chat_id(connect.chat_id)
        result.append(chat)
    return result
