from typing import Optional

from pydantic import BaseSettings


class DbConfig(BaseSettings):
    user: str
    password: str
    db: str
    port: Optional[int] = 5432
    host: Optional[str] = "localhost"

    class Config:
        env_file = ".env"
        env_prefix = "postgres_"


db_config = DbConfig()
