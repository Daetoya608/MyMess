from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey, select, distinct
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

# Для SQLite нужно использовать aiosqlite
DATABASE_URL = "sqlite+aiosqlite:///./client.db"  # файл test.db в текущей директории

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
    chat_name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

    messages = relationship("Message", back_populates="chat")
    connects = relationship("Connect", back_populates="chat")


class Connect(Base):
    __tablename__ = "Connect"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey("Chat.id"), nullable=False)

    chat = relationship("Chat", back_populates="connects")


class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey("Chat.id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
    content_text = Column(Text, nullable=False)

    chat = relationship("Chat", back_populates="messages")


async def add_chat(chat_name: str) -> Chat | None:
    async with new_session() as session:
        new_chat = Chat(chat_name=chat_name)
        session.add(new_chat)
        try:
            await session.commit()
            print(f"Chat {new_chat} was added")
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
            print(f"Connect {new_connect} was added")
            return new_connect
        except IntegrityError:
            await session.rollback()
            print(f"Error: cant add connect {new_connect}")
            return None


async def add_message(sender_id: int, chat_id: int, content_text: str):
    async with new_session() as session:
        new_message = Message(sender_id=sender_id, chat_id=chat_id, content_text=content_text)
        session.add(new_message)
        try:
            await session.commit()
            print(f"\n!!!!\nMessage {new_message} was added\n!!!!\n")
            return new_message
        except IntegrityError:
            await session.rollback()
            print(f"\n???????? Error: cant add message {new_message}\n")
            return None


async def add_message_by_obj(data: dict):
    await add_message(
        sender_id=data["sender_id"],
        chat_id=data["chat_id"],
        content_text=data["content_text"]
    )


async def get_chats_by_user_id(user_id: int) -> list:
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
