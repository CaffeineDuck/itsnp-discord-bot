from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):

    database_url: PostgresDsn
    log_webhook: str

    class Config:
        env_file = ".env"
        fields = {"database_uri": {"env": ["database_uri", "database_url", "database"]}}


conf = Settings()
