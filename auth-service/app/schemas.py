from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str

