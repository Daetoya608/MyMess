from pydantic import BaseModel, Field, ConfigDict

class ContentBase(BaseModel):
    text_content: str = Field(...)

class ContentCreate(ContentBase):
    pass

class ContentResponse(ContentBase):
    config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    sender_id: int = Field(...)
    receiver_id: int
    content_id: int
    content: ContentBase

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    config = ConfigDict(from_attributes=True)

