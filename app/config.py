from pathlib import Path
from typing import Union, Optional
from sqlalchemy.engine import URL

from pydantic_settings import BaseSettings

env_path = Path(__file__).resolve().parent.parent / "properties.env"


class Settings(BaseSettings):
    db_url: Optional[Union[str, URL]] = None

    class Config:
        env_file = env_path


settings = Settings()
