from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn
from pydantic_core import MultiHostUrl
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env')

    # database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # redis
    REDIS_HOST: str
    REDIS_PORT: int
    CACHE_DEFAULT_TTL: int = 60 * 5
    TELEGRAM_EMAIL: str = "id-%d@telegram.org"
    USER_DIALOGUE_INFO: str = "id-%d-model"

    # ngrok
    DOMAIN: str

    # bot
    BOT_TOKEN: str
    BOT_WEBHOOK_PATH: str

    # core_app
    CORE_APP_URL: str
    CORE_APP_AID: str
    DEFAULT_ID_GPT_MODEL: int
    DEFAULT_NAME_GPT_MODEL: str
    FIRST_NAME_DIALOGUE_MODEL: str = "dialogue"
    NAME_DIALOGUE_MODEL: str = "dialogue %d"

    @property
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        return str(MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ))

    @property
    def redis_uri(self) -> RedisDsn:
        return str(MultiHostUrl.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT
        ))

    @property
    def bot_webhook_url(self):
        return self.DOMAIN + self.BOT_WEBHOOK_PATH

    @property
    def core_url(self):
        return self.CORE_APP_URL + self.CORE_APP_AID


settings = Settings()
