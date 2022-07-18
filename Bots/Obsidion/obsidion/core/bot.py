"""Main bot file."""
import json
import logging
import socket
import sys
from datetime import datetime
from enum import IntEnum
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from uuid import UUID

import aiohttp
import aioredis
import asyncpg
import discord
from discord.ext.commands import AutoShardedBot

from .config import get_settings
from .core_commands import Core
from .dev_commands import Dev
from .errors import PlayerNotExistError
from .events import Events
from .settings_cache import AccountManager
from .settings_cache import GuildManager
from .settings_cache import I18nManager


log = logging.getLogger(__name__)


class Obsidion(AutoShardedBot):
    """Main bot class."""

    redis: aioredis.Redis
    db: asyncpg.Pool
    http_session: aiohttp.ClientSession
    _connector: aiohttp.TCPConnector
    _resolver: aiohttp.AsyncResolver
    _invite: Optional[str]
    _invite_bot: Optional[str]

    def __init__(self, *args, **kwargs) -> None:
        """Initialise bot with args passed through."""
        self._shutdown_mode = ExitCodes.CRITICAL
        self.uptime = datetime.now()
        color = get_settings().COLOR.as_rgb_tuple()
        self.color = discord.Color.from_rgb(color[0], color[1], color[2])

        self._i18n_cache = I18nManager(self)
        self._account_cache = AccountManager(self)
        self._guild_cache = GuildManager(self)

        super().__init__(*args, **kwargs)

    async def pre_flight(self) -> None:
        """Pre-flight checks to ensure everything is ready to go."""

        pool = aioredis.ConnectionPool.from_url(
            str(get_settings().REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
        self.redis = aioredis.Redis(connection_pool=pool)
        self.db = await asyncpg.create_pool(str(get_settings().DB))
        self._resolver = aiohttp.AsyncResolver()
        # Use AF_INET as its socket family to prevent HTTPS related
        # problems both locally and in production.
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )

        # timeout
        self._http_timeout = aiohttp.ClientTimeout(total=2)
        self._long_http_timeout = aiohttp.ClientTimeout(total=300)

        # Client.login() will call HTTPClient.static_login()
        # which will create a session using this connector attribute.
        self.http_session = aiohttp.ClientSession(
            connector=self._connector, timeout=self._http_timeout
        )

        # Load important cogs
        self.add_cog(Events(self))
        self.add_cog(Core(self))
        if get_settings().DEV:
            self.add_cog(Dev(self))
        self.on_command_error = self.get_cog("Events").on_command_error

        # load cogs
        self.load_extension("obsidion.cogs.images")
        self.load_extension("obsidion.cogs.info")
        # due to bug with slash_command lib
        # self.load_extension("obsidion.cogs.hypixel")
        self.load_extension("obsidion.cogs.news")
        self.load_extension("obsidion.cogs.fun")
        self.load_extension("obsidion.cogs.minecraft")
        self.load_extension("obsidion.cogs.config")
        self.load_extension("obsidion.cogs.facts")
        self.load_extension("obsidion.cogs.servers")

        if get_settings().BOTLIST_POSTING:
            self.load_extension("obsidion.cogs.botlist")

    async def start(self, *args, **kwargs):
        """
        Overridden start which ensures cog load and other
        pre-connection tasks are handled
        """
        await self.pre_flight()
        return await super().start(*args, **kwargs)

    async def shutdown(self, *, restart: Optional[bool] = False) -> None:
        """Gracefully quit Obsidion.

        The program will exit with code :code:`0` by default.

        Parameters
        ----------
        restart : bool
            If :code:`True`, the program will exit with code :code:`26`. If the
            launcher sees this, it will attempt to restart the bot.

        """
        if not restart:
            self._shutdown_mode = ExitCodes.SHUTDOWN
        else:
            self._shutdown_mode = ExitCodes.RESTART

        await self.close()
        if self.db is not None:
            await self.db.close()
        if self.redis is not None:
            await self.redis.close()
        await self.http_session.close()
        sys.exit(self._shutdown_mode)

    async def mojang_player(
        self, user: discord.User, username: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """Takes in an mc username and tries to convert it to a mc uuid.

        Args:
            username (str): username of player which uuid will be from
            bot (Obsidion): Obsidion bot

        Returns:
            str: uuid of player
        """
        if username is None:
            _uuid = await self._account_cache.get_account(user)
            if _uuid is None:
                raise PlayerNotExistError(None)
            uuid = str(_uuid)
        else:
            username_key = f"username_{username}"
            if await self.redis.exists(username_key):
                uuid = await self.redis.get(username_key)
            else:
                uuid = str(username)
        data: Optional[Dict[str, Any]]
        key = f"player_{str(uuid)}"
        if await self.redis.exists(key):
            data = json.loads(await self.redis.get(key))
        else:
            url = f"https://api.ashcon.app/mojang/v2/user/{str(uuid)}"
            async with self.http_session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                else:
                    data = None
            if data is not None:
                uuid = data["uuid"]
            key = f"player_{uuid}"
            await self.redis.set(key, json.dumps(data), px=28800)
        if data is None:
            raise PlayerNotExistError(str(username))
        else:
            uuid = data["uuid"]
        username_key = f"username_{data['username']}"
        await self.redis.set(username_key, str(uuid), px=28800)
        return data

    def build_embed(
        self, title: str, description: Optional[str] = None, type: Optional[str] = None
    ):
        embed = discord.Embed()
        if description is not None:
            embed.description = description
        embed.set_footer(text="obsidion-dev.com")
        embed.set_author(
            name=title, url="https://obsidion-dev.com", icon_url=self.user.avatar_url
        )
        embed.set_thumbnail(url=self.user.avatar_url)
        embed.timestamp = datetime.utcnow()
        if type == "error":
            embed.colour = discord.Colour.red()
        elif type == "info":
            embed.colour = discord.Colour.blue()
        elif type == "success":
            embed.colour = discord.Colour.green()
        elif type == "warning":
            embed.colour = discord.Colour.orange()
        else:
            embed.colour = self.color

        return embed

    async def get_api_json(
        self,
        key: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        px: int = 600,
    ):
        if await self.redis.exists(key):
            data = json.loads(await self.redis.get(key))
        else:
            async with self.http_session.get(
                f"{get_settings().API_URL}/{endpoint}",
                params=params,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                else:
                    data = None
            await self.redis.set(key, json.dumps(data), px=px)
        return data

    async def get_json(
        self,
        key: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        px: int = 600,
    ):
        if await self.redis.exists(key):
            data = json.loads(await self.redis.get(key))
        else:
            async with self.http_session.get(
                url,
                params=params,
                headers={"User-Agent": "Obsidion Discord Bot"},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                else:
                    data = None
            await self.redis.set(key, json.dumps(data), px=px)
        return data


class ExitCodes(IntEnum):
    # This needs to be an int enum to be used
    # with sys.exit
    CRITICAL = 1
    SHUTDOWN = 0
    RESTART = 26
