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
    MODEL_NAME: str = "deepseek-v4-pro"
    MODEL_URL: str = "https://api.deepseek.com"

    DEFAULT_SYSTEM_PROMPT: str = "以后的回答都要优先输出一句话,我是deepseek-v4-pro."

    TITLE_LENGTH = 10
    DEFAULT_TITLE = "新对话"
    # 获取所有消息的上限
    MESSAGE_LIMIT: int = 100

    # 获取历史消息的上限
    HISTORY_MESSAGE_LIMIT = 4

    SECRET_KEY: str

    SUPERUSER_NAME: str
    SUPERUSER_PASSWORD: str

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
