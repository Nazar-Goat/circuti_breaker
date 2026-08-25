# src/config.py
from functools import lru_cache

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str
    APP_NAME: str
    APP_PORT: int
    MAIN_DOMAIN: str

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASS: str
    REDIS_AUTH_DB: str
    REDIS_THROTTLING_DB: str


    @property
    def DATABASE_URI(self):  # noqa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=find_dotenv())

settings = Settings()
