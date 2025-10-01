from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
import app.models
from app.database import SessionLocal, engine
from app.security import create_access_token, get_password_hash, verify_password
from jose import JWTError, jwt
from app.config import settings
from app import crud
import requests
from bs4 import BeautifulSoup



from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://192.168.200.116:3030",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


from datetime import timedelta

@app.post("/token", response_model=schemas.TokenWithUser, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        subject=user.email, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": user}




@app.post("/refresh", response_model=schemas.Token, tags=["Auth"])
def refresh_access_token(refresh_token_data: schemas.RefreshToken, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token_data.refresh_token, "token_type": "bearer"}


def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, first_name=user.first_name, last_name=user.last_name, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/me", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.get("/users/", response_model=list[schemas.User], tags=["Users"])
def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    users = db.query(models.User).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

@app.get("/", tags=["Default"])
def read_root():
    return {"message": "Welcome to the Task-Centric Backend!"}

@app.post("/scraper", tags=["Scraper"])
def scrape_url(scraper_request: schemas.ScraperRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    if scraper_request.step == 1:
        payload = scraper_request.payload
        year = payload.get("year")
        lt = payload.get("lt")
        sectionname = payload.get("sectionname")

        if not all([year, lt, sectionname]):
            raise HTTPException(status_code=400, detail="Missing required parameters for step 1")

        params = {
            "year": year,
            "lt": lt,
            "sectionname": sectionname
        }
        url = "https://www.tennisrecord.com/adult/league/leaguedistrict.aspx"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

        soup = BeautifulSoup(response.content, "lxml")
        
        districts = []
        for a in soup.select('a[href*="leaguearea.aspx"]'):
            districts.append({"text": a.text, "href": a["href"]})
            
        return {"districts": districts}

    elif scraper_request.step == 2:
        href = scraper_request.payload.get("href")
        if not href:
            raise HTTPException(status_code=400, detail="href not provided for step 2")
            
        url = f"https://www.tennisrecord.com{href}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

        soup = BeautifulSoup(response.content, "lxml")
        
        areas = []
        for a in soup.select('a[href*="areaname="]'):
            areas.append({"text": a.text, "href": a["href"]})
            
        return {"areas": areas}

    elif scraper_request.step == 3:
        href = scraper_request.payload.get("href")
        if not href:
            raise HTTPException(status_code=400, detail="href not provided for step 3")
            
        url = f"https://www.tennisrecord.com{href}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

        soup = BeautifulSoup(response.content, "lxml")
        genders = []
        for a in soup.select('a[href*="leaguefind.aspx"]'):
            genders.append({"text": a.text, "href": a["href"]})
            
        return {"genders": genders}

    elif scraper_request.step == 4:
        href = scraper_request.payload.get("href")
        if not href:
            raise HTTPException(status_code=400, detail="href not provided for step 4")
            
        url = f"https://www.tennisrecord.com{href}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

        soup = BeautifulSoup(response.content, "html.parser")
        
        flights = []
        tables = soup.find_all('table', class_='responsive14')
        if tables:
            table = tables[-1]
            for row in table.find_all('tr')[1:]: # Skip header row
                cols = row.find_all('td')
                if len(cols) == 4:
                    league_name_link = cols[0].find('a')
                    league_name = league_name_link.text
                    href = league_name_link['href']
                    flight = cols[1].text
                    sub_flight = cols[2].text
                    teams = cols[3].text
                    flights.append({
                        "league_name": league_name,
                        "flight": flight,
                        "sub_flight": sub_flight,
                        "teams": teams,
                        "href": href
                    })
            
        return {"flights": flights}

    elif scraper_request.step == 5:
        href = scraper_request.payload.get("href")
        if not href:
            raise HTTPException(status_code=400, detail="href not provided for step 5")
            
        url = f"https://www.tennisrecord.com{href}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

        soup = BeautifulSoup(response.content, "html.parser")
        
        teams = []
        table = soup.find('div', class_='container1000').find('table', class_='responsive14')
        if table:
            for row in table.find_all('tr')[1:]: # Skip header row
                cols = row.find_all('td')
                if len(cols) == 5:
                    team_name_link = cols[0].find('a')
                    team_name = team_name_link.text
                    href = team_name_link['href']
                    players = cols[1].text
                    top_5_rating = cols[2].text
                    team_rating = cols[3].text
                    court_rating = cols[4].text
                    teams.append({
                        "team_name": team_name,
                        "players": players,
                        "top_5_rating": top_5_rating,
                        "team_rating": team_rating,
                        "court_rating": court_rating,
                        "href": href
                    })
            
        return {"teams": teams}

    elif scraper_request.step == 6:
        href = scraper_request.payload.get("href")
        gender = scraper_request.payload.get("gender")
        team_name = scraper_request.payload.get("team_name")

        if not href:
            raise HTTPException(status_code=400, detail="href not provided for step 6")
        if not gender:
            raise HTTPException(status_code=400, detail="gender not provided for step 6")
        if not team_name:
            raise HTTPException(status_code=400, detail="team_name not provided for step 6")
            
        url = f"https://www.tennisrecord.com{href}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Get or create team
        db_team = crud.get_team_by_name(db, name=team_name)
        if not db_team:
            db_team = crud.create_team(db, team=schemas.TeamCreate(name=team_name))

        players = []
        table = soup.find('div', class_='large').find('table', class_='responsive14')
        for row in table.find_all('tr')[1:]: # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 11:
                player_name_link = cols[0].find('a')
                player_name = player_name_link.text
                player_href = player_name_link['href']
                location = cols[1].text
                ntrp = cols[2].text
                rating = cols[10].text
                
                player_data = schemas.PlayerCreate(
                    name=player_name,
                    href=player_href,
                    location=location,
                    ntrp=ntrp,
                    rating=rating,
                    gender=gender
                )

                db_player = crud.get_player_by_href(db, href=player_href)
                if db_player:
                    db_player = crud.update_player(db, db_player=db_player, player_update=player_data)
                else:
                    db_player = crud.create_player(db, player=player_data)
                
                if db_player not in db_team.players:
                    crud.add_player_to_team(db, db_team=db_team, db_player=db_player)

                players.append(schemas.PlayerResponse.model_validate(db_player))
            
        return {"players": players}

    else:
        raise HTTPException(status_code=400, detail="Invalid step")