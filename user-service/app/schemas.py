from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(...)
    nickname: str = Field(...)
    email: str = Field(...)
    info_about_yourself: str = Field(default="")


class UserCreate(UserBase):
    pass  # Тут можно добавить дополнительные проверки (например, длина username)


class UserUpdate(BaseModel):
    nickname: str | None = None
    info_about_yourself: str | None = None


class UserResponse(UserBase):
    id: int

    config = ConfigDict(from_attributes=True)