from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    role: str | None = None

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

class TokenWithUser(Token):
    user: User

class TokenData(BaseModel):
    email: str | None = None

class RefreshToken(BaseModel):
    refresh_token: str

class ScraperRequest(BaseModel):
    url: str | None = None
    step: int
    payload: dict | None = None

class PlayerBase(BaseModel):
    name: str
    href: str
    location: str
    ntrp: str
    rating: str
    gender: str

class PlayerCreate(PlayerBase):
    pass

class PlayerResponse(PlayerBase):
    id: int

    class Config:
        from_attributes = True

class Player(PlayerBase):
    id: int
    teams: list['Team'] = [] # Forward reference

    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    players: list[Player] = []

    class Config:
        from_attributes = True

Player.model_rebuild()
