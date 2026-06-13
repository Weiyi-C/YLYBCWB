from pydantic import BaseModel, Field
from datetime import datetime


class FamilyResponse(BaseModel):
    id: str
    name: str
    invite_code: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class JoinFamilyRequest(BaseModel):
    invite_code: str


class MemberResponse(BaseModel):
    id: str
    user_id: str
    username: str
    nickname: str | None
    display_name: str | None
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class MemberUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=50)
    role: str | None = Field(None, pattern="^(admin|member)$")
