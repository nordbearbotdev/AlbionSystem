"""Settings management for the bot."""
import logging
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from pydantic import BaseSettings
from pydantic import HttpUrl
from pydantic import PositiveInt
from pydantic import PostgresDsn
from pydantic import RedisDsn
from pydantic import UUID4
from pydantic import validator
from pydantic.color import Color

log = logging.getLogger("obsidion")


class Settings(BaseSettings):
    """Bot config settings."""

    DISCORD_TOKEN: str
    SERVER_NAME: str
    API_URL: HttpUrl
    HYPIXEL_API_TOKEN: UUID4
    ACTIVITY: str = "for @Obsidion help"
    STACK_TRACE_CHANNEL: PositiveInt
    POSTGRES_SERVER: Optional[str]
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_DB: Optional[str]
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True)
    def validate_db_url(cls, v) -> Union[HttpUrl, None]:  # noqa: B902,N805
        if v == "":
            return None
        return v

    DB: Optional[PostgresDsn] = None

    @validator("DB", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]  # noqa: B902,N805
    ) -> Any:
        if isinstance(v, str):
            return v
        if values.get("DATABASE_URL") is not None:
            return values.get("DATABASE_URL")
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_URL: RedisDsn
    DEV: bool = False
    COLOR: Color = Color("0x00FF00")
    LOGLEVEL: Optional[str] = "INFO"
    SENTRY: Optional[HttpUrl]

    @validator("SENTRY", pre=True)
    def validate_sentry(cls, v) -> Union[HttpUrl, None]:  # noqa: B902,N805
        if v == "":
            return None
        return v

    BOTLIST_POSTING: bool = False
    DBL_TOKEN: Optional[str]
    DISCORDBOTLIST_TOKEN: Optional[str]
    BOTSFORDISCORD_TOKEN: Optional[str]
    DISCORDBOATS_TOKEN: Optional[str]
    DISCORDLABS_TOKEN: Optional[str]
    BOTSONDISCORD_TOKEN: Optional[str]

    class Config:
        """Config for pydantic."""

        # Env will always take priority and is recommended for production
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get settings object and cache it."""
    return Settings()
