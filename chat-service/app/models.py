
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from database import Base, new_session
from sqlalchemy.orm import relationship


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
    created_at = Column(DateTime, default=func.now())

    content = relationship("Content")


