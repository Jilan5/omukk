import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int
    SQLALCHEMY_DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"


settings = Settings()
