from pydantic_settings import BaseSettings
from pathlib import Path
from loguru import logger
import os


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    recognition_api_key: str = "test-key"
    video_api_key: str = "test-key"
    recognition_api_url: str = ""
    video_generation_api_url: str = ""
    broker_url: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()


def init_env():
    env_example = Path(".env.example")
    env_file = Path(".env")
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        logger.info("Created .env file from example")


# Configure logger
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.info("Logger initialized")