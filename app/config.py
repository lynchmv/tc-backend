from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    SECRET_KEY: str = "a_very_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        pass

settings = Settings()
