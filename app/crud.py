from sqlalchemy.orm import Session

from . import models, schemas

def get_team_by_name(db: Session, name: str):
    return db.query(models.Team).filter(models.Team.name == name).first()

def create_team(db: Session, team: schemas.TeamCreate):
    db_team = models.Team(name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def get_player_by_href(db: Session, href: str):
    return db.query(models.Player).filter(models.Player.href == href).first()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, db_player: models.Player, player_update: schemas.PlayerCreate):
    for key, value in player_update.dict().items():
        setattr(db_player, key, value)
    db.commit()
    db.refresh(db_player)
    return db_player

def add_player_to_team(db: Session, db_team: models.Team, db_player: models.Player):
    db_team.players.append(db_player)
    db.commit()
