from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import TimestampedBase

# Association table for the many-to-many relationship between players and teams
player_team_association = Table('player_team_association', TimestampedBase.metadata,
    Column('player_id', Integer, ForeignKey('players.id')),
    Column('team_id', Integer, ForeignKey('teams.id'))
)

class User(TimestampedBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

class Team(TimestampedBase):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    players = relationship("Player",
                    secondary=player_team_association,
                    back_populates="teams")

class Player(TimestampedBase):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    href = Column(String, unique=True, index=True)
    location = Column(String)
    ntrp = Column(String)
    rating = Column(String)
    gender = Column(String)
    teams = relationship("Team",
                   secondary=player_team_association,
                   back_populates="players")
