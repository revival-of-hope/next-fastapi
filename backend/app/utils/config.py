from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    computed_field,
    PostgresDsn,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_URL: str = "https://api.deepseek.com"

    SECRET_KEY: str

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""

    @computed_field
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()  # type: ignore
