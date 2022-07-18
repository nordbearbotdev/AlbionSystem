"""Images cog."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import TYPE_CHECKING
from typing import Union

import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext import tasks
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion

log = logging.getLogger(__name__)

_ = Translator("News", __file__)


@cog_i18n(_)
class News(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot
        self.last_media_data = datetime.now(timezone.utc)
        self.last_media_url = ""
        self.last_java_version_data = datetime.now(timezone.utc)
        self.mojang_service: Dict[str, str] = {}
        self.autopost.start()

    async def get_status(self) -> Union[discord.Embed, None]:
        data = await self.bot.get_api_json("status", "mojang/check")
        if data is None:
            return None
        embed = discord.Embed(colour=self.bot.color)
        embed.set_author(name="Mojang service downtime")
        em = 0
        for service in data:
            if data[service] != "green" and service not in self.mojang_service:
                em = 1
                embed.add_field(name=_("Downtime"), value=service)
            elif data[service] == "green" and service in self.mojang_service:
                em = 1
                embed.add_field(name=_("Back Online"), value=service)
        if em == 0:
            return None
        return embed

    async def get_media(self) -> Union[discord.Embed, None]:
        """Get rss media."""
        data = await self.bot.get_json(
            "news",
            "https://www.minecraft.net/content/minecraft-net/_jcr_content.articles.grid?tileselection=auto",
        )
        if data is None:
            return None

        latest_post = data["article_grid"][0]

        # run checks to see wether it should be posted

        time = datetime.strptime(
            latest_post["publish_date"], "%d %B %Y %X %Z"
        ).astimezone(timezone.utc)

        if time <= self.last_media_data:
            return None

        if latest_post["article_url"] != self.last_media_url:
            return None

        self.last_media_data = time
        self.last_media_url = latest_post["article_url"]

        post_url = f"https://minecraft.net{latest_post['article_url']}"

        async with self.bot.http_session.get(
            post_url, headers={"User-Agent": "Obsidion Discord Bot"}
        ) as resp:
            text = await resp.text()
        soup = BeautifulSoup(text, "lxml")

        author = soup.find("dl", class_="attribution__details").dd.string
        text = soup.find("div", class_="end-with-block").p.text
        url = f"https://minecraft.net{latest_post['default_tile']['image']['imageURL']}"
        embed = discord.Embed(
            title=soup.find("h1").string,
            description=text,
            colour=self.bot.color,
            url=post_url,
        )

        # add categories
        embed.set_image(url=url)
        try:
            author_image = (
                f"https://www.minecraft.net"
                f"{soup.find('img', id='author-avatar').get('src')}"
            )
            embed.set_thumbnail(url=author_image)
        except AttributeError:
            pass
        embed.add_field(name=_("Category"), value=latest_post["primary_category"])
        embed.add_field(name=_("Author"), value=author)
        embed.add_field(
            name=_("Publish Date"),
            value=datetime.strftime(
                datetime.strptime(latest_post["publish_date"], "%d %B %Y %X %Z"),
                "%d/%m/%Y",
            ),
        )

        # create footer
        embed.set_footer(text=_("Article Published"))
        embed.timestamp = time

        # create title
        embed.set_author(
            name=_("New Article on Minecraft.net"),
            url=post_url,
            icon_url=(
                "https://www.minecraft.net/etc.clientlibs/minecraft"
                "/clientlibs/main/resources/img/menu/menu-buy--reversed.gif"
            ),
        )

        return embed

    async def get_java_releases(self) -> Union[discord.Embed, None]:
        data = await self.bot.get_json(
            "versions", "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        )
        if data is None:
            return None

        last_release = data["versions"][0]

        format = "%Y-%m-%dT%H:%M:%S%z"
        time = datetime.strptime(last_release["time"], format)
        if time <= self.last_java_version_data:
            return None

        embed = discord.Embed(
            colour=self.bot.color,
        )

        embed.add_field(name=_("Name"), value=last_release["id"])
        embed.add_field(
            name=_("Package URL"),
            value=_("[Package URL]({url})").format(url=last_release["url"]),
        )
        embed.add_field(
            name=_("Minecraft Wiki"),
            value=_(
                "[Minecraft Wiki](https://minecraft.fandom.com/Java_Edition_{id})"
            ).format(id=last_release["id"]),
        )

        embed.set_footer(text=_("Article Published"))
        embed.timestamp = time
        self.last_java_version_data = time
        embed.set_author(
            name=_("New Minecraft Java Edition Snapshot"),
            url=f"https://minecraft.fandom.com/Java_Edition_{last_release['id']}",
            icon_url=(
                "https://www.minecraft.net/etc.clientlibs/minecraft"
                "/clientlibs/main/resources/img/menu/menu-buy--reversed.gif"
            ),
        )
        return embed

    async def post_content(
        self, embed: Union[discord.Embed, None], channels: Dict[str, Any], category: str
    ) -> None:
        if embed is not None and category in channels:
            for _channel in channels[category]:
                channel = self.bot.get_channel(_channel)
                if (
                    channel is not None
                    and channel.permissions_for(channel.server.me).send_messages
                ):
                    message = await channel.send(embed=embed)
                    try:
                        await message.publish()
                    except discord.errors.Forbidden:
                        pass

    @tasks.loop(minutes=10)
    async def autopost(self) -> None:
        posts = await self.bot.db.fetch("SELECT news FROM guild WHERE news IS NOT NULL")
        channels: Dict[str, List[int]] = {}
        for server in posts:
            n = json.loads(server["news"])
            for key in n.keys():
                if n[key] is not None:
                    if key in channels:
                        channels[key].append(n[key])
                    else:
                        channels[key] = [n[key]]
        try:
            release_embed = await self.get_java_releases()
            await self.post_content(release_embed, channels, "release")
        except Exception as e:
            log.exception(type(e).__name__, exc_info=e)
        try:
            article_embed = await self.get_media()
            await self.post_content(article_embed, channels, "article")
        except Exception as e:
            log.exception(type(e).__name__, exc_info=e)
        # try:
        #     status_embed = await self.get_status()
        #     await self.post_content(status_embed, channels, "status")
        # except Exception as e:
        #     log.exception(type(e).__name__, exc_info=e)

    def cog_unload(self) -> None:
        """Stop news posting tasks on cog unload."""
        self.autopost.cancel()
