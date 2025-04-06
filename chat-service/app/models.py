from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey, DateTime, func, select, distinct
from sqlalchemy.exc import IntegrityError
from database import Base, new_session
from sqlalchemy.orm import relationship


class Chat(Base):
    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True, index=True)
    chat_name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    messages = relationship("Message", back_populates="chat")
    connects = relationship("Connect", back_populates="chat")


class Connect(Base):
    __tablename__ = "Connect"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey("Chat.id"), nullable=False)

    chat = relationship("Chat", back_populates="users")


class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey("Chat.id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now())
    content_text = Column(Text, nullable=False)

    chat = relationship("Chat", back_populates="messages")


async def add_chat(chat_name: str):
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
            print(f"Message {new_message} was added")
            return new_message
        except IntegrityError:
            await session.rollback()
            print(f"Error: cant add message {new_message}")
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
        return result.scalars().all()


async def get_unique_user_ids():
    async with new_session() as session:
        result = await session.execute(
            select(distinct(Connect.user_id))
        )
        return result.scalars().all()


# async def get_content_by_id(content_id: int) -> Content | None:
#     async with new_session() as session:
#         content = await session.get(Content, content_id)
#         return content
#
#
# async def add_message(sender_id, receiver_id, content_id):
#     async with new_session() as session:
#         new_message =  Message(sender_id=sender_id, receiver_id=receiver_id, content_id=content_id)
#         session.add(new_message)
#         try:
#             await session.commit()
#             print(f"Message {new_message} was added")
#             return new_message.id
#         except IntegrityError:
#             await session.rollback()
#             print(f"Error: cant add message")
#             return 0


# async def get_message_by_id(message_id: int) -> Message | None:
#     async with new_session() as session:
#         message = await session.get(Message, message_id)
#         return message
#
#
# async def get_unread_messages_for_user(user_id):
#     async with new_session() as session:
#         result = await session.execute(select(Message).where(Message.receiver_id == user_id and
#                                                        Message.is_read == False))
#         return result.scalars().all()
#
#
# async def get_chat_by_id(chat_id: int) -> Chat | None:
#     async with new_session() as session:
#         chat = await session.get(Chat, chat_id)
#         return chat
#
#
# async def add_content_and_message(message_data: dict):
#     try:
#         content_id = await add_content(message_data["content"]["text_content"])
#         if content_id == 0:
#             return None
#         message_id = await add_message(
#             sender_id=message_data["sender_id"],
#             receiver_id=message_data["receiver_id"],
#             content_id=content_id
#         )
#         if message_id == 0:
#             return None
#         return message_id
#     except KeyError:
#         return None
