from pydantic import BaseSettings


class Settings(BaseSettings):
    auth_key: str
    db_url: str

    class Config:
        env_prefix = "qdam_"
        env_file = ".env"


settings = Settings()
