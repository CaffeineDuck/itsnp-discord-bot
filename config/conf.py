from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):

    log_webhook: str

    class Config:
        env_file = ".env"


conf = Settings()
