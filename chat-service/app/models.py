
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey, DateTime, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from database import Base, new_session
from sqlalchemy.orm import relationship


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    first_user_id = Column(Integer, nullable=False)
    second_user_id = Column(Integer, nullable=False)

    messages = relationship("Message", back_populates="chat")



class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    text_content = Column(Text, nullable=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now())

    content = relationship("Content")
    chat = relationship("Chat", back_populates="messages")


async def add_content(text: str):
    async with new_session() as session:
        new_content = Content(text_content=text)
        session.add(new_content)
        try:
            await session.commit()
            print(f"Content {new_content} was added")
            return new_content.id
        except IntegrityError:
            await session.rollback()
            print("Error: cant add content")
            return 0


async def get_content_by_id(content_id: int) -> Content | None:
    async with new_session() as session:
        content = await session.get(Content, content_id)
        return content


async def add_message(sender_id, receiver_id, content_id):
    async with new_session() as session:
        new_message =  Message(sender_id=sender_id, receiver_id=receiver_id, content_id=content_id)
        session.add(new_message)
        try:
            await session.commit()
            print(f"Message {new_message} was added")
            return new_message.id
        except IntegrityError:
            await session.rollback()
            print(f"Error: cant add message")
            return 0


async def get_message_by_id(message_id: int) -> Message | None:
    async with new_session() as session:
        message = await session.get(Message, message_id)
        return message


async def get_unread_messages_for_user(user_id):
    async with new_session() as session:
        result = await session.execute(select(Message).where(Message.receiver_id == user_id and
                                                       Message.is_read == False))
        return result.scalars().all()


async def get_chat_by_id(chat_id: int) -> Chat | None:
    async with new_session() as session:
        chat = await session.get(Chat, chat_id)
        return chat


async def add_content_and_message(message_data: dict):
    try:
        content_id = await add_content(message_data["content"]["text_content"])
        if content_id == 0:
            return None
        message_id = await add_message(
            sender_id=message_data["sender_id"],
            receiver_id=message_data["receiver_id"],
            content_id=content_id
        )
        if message_id == 0:
            return None
        return message_id
    except KeyError:
        return None
