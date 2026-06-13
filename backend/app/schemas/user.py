from pydantic import BaseModel, Field
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    nickname: str | None
    avatar_url: str | None
    phone: str | None
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, max_length=50)
    avatar_url: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, max_length=20)
