"""Database and cache."""
from __future__ import annotations

import json
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import Union
from uuid import UUID

import discord

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion

NewsType = TypedDict(
    "NewsType",
    {
        "release": Optional[int],
        "snapshot": Optional[int],
        "article": Optional[int],
        "status": Optional[int],
    },
)


class I18nManager:
    def __init__(self, bot: Obsidion) -> None:
        self._bot = bot

    async def get_locale(self, guild: Union[discord.Guild, None]) -> str:
        """Get the guild locale from the cache"""
        if not guild:
            return "en-US"
        gid = guild.id
        key = f"locale_{gid}"
        redis = await self._bot.redis.exists(key)
        if redis:
            locale = await self._bot.redis.get(key)
        else:
            db_locale = await self._bot.db.fetchval(
                "SELECT locale FROM guild WHERE id = $1", gid
            )
            if db_locale:
                locale = db_locale
            else:
                locale = "en-US"
            await self._bot.redis.set(key, locale, px=28800)

        return locale

    async def set_locale(self, guild: discord.Guild, locale: Union[str, None]) -> None:
        """Set the locale in the config and cache"""
        gid = guild.id

        key = f"locale_{gid}"
        if await self._bot.db.fetch("SELECT locale FROM guild WHERE id = $1", gid):
            await self._bot.db.execute(
                "UPDATE guild SET locale = $1 WHERE id = $2", locale, gid
            )
        else:
            await self._bot.db.execute(
                "INSERT INTO guild (id, locale) VALUES ($1, $2)",
                gid,
                locale,
            )
        await self._bot.redis.set(key, str(locale), px=28800)

    async def get_regional_format(
        self, guild: Union[discord.Guild, None]
    ) -> Optional[str]:
        """Get the regional format from the cache"""
        if not guild:
            return "en-US"
        gid = guild.id
        key = f"regional_{gid}"
        redis = await self._bot.redis.exists(key)
        if redis:
            regional = await self._bot.redis.get(key)
        else:
            db_regional = await self._bot.db.fetchval(
                "SELECT regional FROM guild WHERE id = $1", gid
            )
            if db_regional:
                regional = db_regional
            else:
                regional = "en-US"
            await self._bot.redis.set(key, regional, px=28800)

        return regional

    async def set_regional_format(
        self, guild: discord.Guild, regional_format: Union[str, None]
    ) -> None:
        """Set the regional format in the config and cache"""
        gid = guild.id

        key = f"regional_{gid}"
        if await self._bot.db.fetch("SELECT regional FROM guild WHERE id = $1", gid):
            await self._bot.db.execute(
                "UPDATE guild SET regional = $1 WHERE id = $2", regional_format, gid
            )
        else:
            await self._bot.db.execute(
                "INSERT INTO guild (id, regional) VALUES ($1, $2)",
                gid,
                regional_format,
            )
        await self._bot.redis.set(key, str(regional_format), px=28800)


class AccountManager:
    def __init__(self, bot: Obsidion):
        self._bot = bot

    async def get_account(self, user: discord.User) -> Union[UUID, None]:
        uid = user.id
        key = f"account_{uid}"
        redis = await self._bot.redis.exists(key)
        if redis:
            uuid = await self._bot.redis.get(key)
            if uuid == "None":
                uuid = None
            if uuid is not None:
                uuid = UUID(str(uuid))
        else:
            uuid = await self._bot.db.fetchval(
                "SELECT uuid FROM account WHERE id = $1", uid
            )
            await self._bot.redis.set(key, str(uuid), px=28800)
        return uuid

    async def set_account(
        self, user: discord.User, uuid: Optional[Union[UUID, str]] = None
    ) -> None:
        uid = user.id
        key = f"account_{uid}"
        if await self._bot.db.fetch("SELECT uuid FROM account WHERE id = $1", uid):
            await self._bot.db.execute(
                "UPDATE account SET uuid = $1 WHERE id = $2",
                uuid,
                uid,
            )
        else:
            await self._bot.db.execute(
                "INSERT INTO account (id, uuid) VALUES ($1, $2)",
                uid,
                uuid,
            )
        await self._bot.redis.set(key, str(uuid), px=28800)


class GuildManager:
    def __init__(self, bot: Obsidion) -> None:
        self._bot = bot

    async def get_server(self, guild: discord.Guild) -> Union[str, None]:
        gid = guild.id
        key = f"server_{gid}"
        redis = await self._bot.redis.exists(key)
        if redis:
            server = await self._bot.redis.get(key)
            if server == "None":
                server = None
        else:
            server = await self._bot.db.fetchval(
                "SELECT server FROM guild WHERE id = $1", gid
            )
            await self._bot.redis.set(key, str(server), px=28800)
        return server

    async def set_server(
        self, guild: discord.Guild, server: Optional[str] = None
    ) -> None:
        gid = guild.id
        key = f"server_{gid}"
        if await self._bot.db.fetch("SELECT server FROM guild WHERE id = $1", gid):
            await self._bot.db.execute(
                "UPDATE guild SET server = $1 WHERE id = $2",
                server,
                gid,
            )
        else:
            await self._bot.db.execute(
                "INSERT INTO guild (id, server) VALUES ($1, $2)",
                gid,
                server,
            )
        await self._bot.redis.set(key, str(server), px=28800)

    async def get_news(self, guild: discord.Guild) -> Optional[NewsType]:
        gid = guild.id
        key = f"news_{gid}"
        redis = await self._bot.redis.exists(key)
        if redis:
            server = json.loads(await self._bot.redis.get(key))
        else:
            server = await self._bot.db.fetchval(
                "SELECT news FROM guild WHERE id = $1", gid
            )
            if server is not None:
                server = json.loads(server)
            await self._bot.redis.set(key, json.dumps(server), px=28800)
        return server

    async def set_news(self, guild: discord.Guild, news: Optional[NewsType]) -> None:
        gid = guild.id
        key = f"news_{gid}"
        if await self._bot.db.fetch("SELECT news FROM guild WHERE id = $1", gid):
            await self._bot.db.execute(
                "UPDATE guild SET news = $1 WHERE id = $2",
                json.dumps(news),
                gid,
            )
        else:
            await self._bot.db.execute(
                "INSERT INTO guild (id, news) VALUES ($1, $2)",
                gid,
                json.dumps(news),
            )
        await self._bot.redis.set(key, json.dumps(news), px=28800)
