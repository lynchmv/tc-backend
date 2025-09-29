from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class RefreshToken(BaseModel):
    refresh_token: str
