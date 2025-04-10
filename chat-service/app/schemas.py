from pydantic import BaseModel, Field, ConfigDict

class ContentBase(BaseModel):
    text_content: str = Field(...)

class ContentCreate(ContentBase):
    pass

class ContentResponse(ContentBase):
    model_config = { "from_attributes": True }


class MessageBase(BaseModel):
    sender_id: int = Field(...)
    receiver_id: int
    content_id: int = Field(exclude=True)
    content: ContentBase

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    model_config = { "from_attributes": True }

class SendRequest(BaseModel):
    token: str
    sender_id: int
    receiver_id: int
    content: ContentCreate
