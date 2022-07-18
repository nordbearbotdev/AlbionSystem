"""Info cog."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from obsidion.core import get_settings
from obsidion.core.errors import ProvideServerError
from obsidion.core.errors import ServerUnavailableError
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion

log = logging.getLogger(__name__)

_ = Translator("Info", __file__)


@cog_i18n(_)
class Info(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot

    @cog_ext.cog_slash(
        name="profile",
        description="View a players Minecraft UUID, Username history and skin.",
        options=[
            create_option(
                name="username",
                description="Username of player defaults to your linked username.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def profile(self, ctx: SlashContext, username: str = None) -> None:
        profile_info = await self.bot.mojang_player(ctx.author, username)
        if username is None:
            username = profile_info["username"]
        uuid: str = profile_info["uuid"]
        names = profile_info["username_history"]
        h = 0
        for c in uuid.replace("-", ""):
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        skin_type = "Alex"
        if (((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000) % 2 == 0:
            skin_type = "Steve"

        name_list = ""
        for name in names[1:]:
            name_list += ("**{number}.** `{username}` - {date}\n").format(
                number=len(names) - (names.index(name) - 1),
                username=name["username"],
                date=(
                    datetime.strptime(name["changed_at"], "%Y-%m-%dT%X.%fZ")
                ).strftime("%b %d, %Y"),
            )
        name_list += _("**1.** `{original}` - First Username").format(
            original=names[0]["username"]
        )

        embed = self.bot.build_embed(
            _("Minecraft profile for {username}").format(
                username=names[-1]["username"]
            ),
            "Profile Information",
        )

        embed.add_field(
            name="Account",
            inline=False,
            value=_("Full UUID: `{uuid}`\nShort UUID: `{short}`").format(
                uuid=uuid, short=uuid.replace("-", "")
            ),
        )
        embed.add_field(
            name="Textures",
            inline=True,
            value=_(
                "Skin: [Open Skin](https://visage.surgeplay.com/skin/512/"
                "{uuid})\nSkin Type: `{skin_type}`\nSkin History: [link]"
                "({skin_history})\nSlim: `{slim}`\nCustom: `{custom}`"
                "\nCape: `{cape}`"
            ).format(
                uuid=uuid,
                skin_type=skin_type,
                skin_history=f"https://mcskinhistory.com/player/{username}",
                slim=profile_info["textures"]["slim"]
                if "slim" in profile_info["textures"]
                else False,
                custom=profile_info["textures"]["custom"]
                if "custom" in profile_info["textures"]
                else False,
                cape=True if "cape" in profile_info["textures"] else False,
            ),
        )
        embed.add_field(
            name=_("Information"),
            inline=True,
            value=_(
                "Username Changes: `{changes}`\nNamemc: [link]({namemc})"
                "\nLegacy: `{legacy}`\nDemo: `{demo}`"
            ).format(
                changes=len(names) - 1,
                namemc=f"https://namemc.com/profile/{uuid}",
                legacy=profile_info["legacy"] if "legacy" in profile_info else False,
                demo=profile_info["demo"] if "demo" in profile_info else False,
            ),
        )
        embed.add_field(
            name=_("Name History"),
            inline=False,
            value=name_list,
        )
        embed.set_thumbnail(url=(f"https://visage.surgeplay.com/bust/{uuid}"))
        await ctx.send(embed=embed)

    @staticmethod
    def get_server(ip: str, port: Optional[int] = None) -> Tuple[str, Optional[int]]:
        """Returns the server icon."""
        if ":" in ip:  # deal with them providing port in string instead of separate
            address, _port = ip.split(":")
            return (address, int(_port))
        return (ip, port)

    @cog_ext.cog_slash(
        name="server",
        description="Minecraft server info.",
        options=[
            create_option(
                name="address",
                description="Address of server defaults to your linked server.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="port",
                description="port of server defaults to that of your linked server.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def server(
        self, ctx: SlashContext, address: str = None, port: int = None
    ) -> None:
        if address is None and ctx.guild is not None:
            address = await self.bot._guild_cache.get_server(ctx.guild)
        if address is None:
            raise ProvideServerError()
        if len(address.split(":")) > 2:
            raise ProvideServerError()
        server_ip, port = self.get_server(address, port)
        key = f"server_{server_ip}:{port}"
        endpoint = "server/java"
        params: Dict[str, Union[int, str]] = (
            {"server": address} if port is None else {"server": address, "port": port}
        )
        data = await self.bot.get_api_json(key, endpoint, params)
        if data is None:
            raise ServerUnavailableError(address)
        embed = self.bot.build_embed(
            _("Java Server: {server_ip}").format(server_ip=server_ip),
            description=data["motd"]["clean"][0],
        )

        embed.add_field(
            name="Players",
            value=_("Online: `{online}` \n " "Maximum: `{maximum}`").format(
                online=data["players"]["online"], maximum=data["players"]["max"]
            ),
        )
        embed.add_field(
            name=_("Version"),
            value=_(
                "Java Edition \n Running: `{version}` \n" "Protocol: `{protocol}`"
            ).format(version=data["version"], protocol=data["protocol"]),
        )
        if data["icon"]:
            url = f"{get_settings().API_URL}/server/javaicon?server={server_ip}"
            if port is not None:
                url += f"&port={port}"
            embed.set_thumbnail(url=url)
        else:
            embed.set_thumbnail(
                url=(
                    "https://media.discordapp.net/attachments/493764139290984459"
                    "/602058959284863051/unknown.png"
                )
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="serverpe",
        description="Get information from a Minecraft Bedrock server.",
        options=[
            create_option(
                name="address",
                description="Address of server defaults to your linked server.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="port",
                description="port of server defaults to that of your linked server.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def serverpe(self, ctx: SlashContext, address: str, port: int = None) -> None:
        if len(address.split(":")) > 2:
            raise ProvideServerError()
        address, port = self.get_server(address, port)
        key = f"server_{address}:{port}"
        endpoint = "server/bedrock"
        params: Dict[str, Union[str, int]] = (
            {"server": address} if port is None else {"server": address, "port": port}
        )
        data = await self.bot.get_api_json(key, endpoint, params)
        if data is None:
            raise ServerUnavailableError(address)
        embed = self.bot.build_embed(
            _("Bedrock Server: {address}").format(address=address), "Server Information"
        )
        embed.add_field(name=_("Description"), value="\n".join(data["motd"]))

        embed.add_field(
            name=_("Players"),
            value=_("Online: `{player_count}` \n " "Maximum: `{player_max}`").format(
                player_count=data["player_count"], player_max=data["player_max"]
            ),
        )
        embed.add_field(
            name=_("Version"),
            value=_(
                "Bedrock Edition \n Running: `{version}` \n" "Protocol: `{protocol}`"
            ).format(version=data["protocol_version"], protocol=data["protocol_name"]),
            inline=False,
        )
        embed.add_field(
            name=_("Info"),
            value=_("Gamemode: `{gamemode}` \n" "Latency: `{latency}`").format(
                version=data["gamemode"], protocol=data["latency"]
            ),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="status", description="Check the status of all the Mojang services."
    )
    async def status(self, ctx: SlashContext) -> None:
        await ctx.defer()
        async with self.bot.http_session.get(
            f"{get_settings().API_URL}/mojang/check"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
            else:
                data = None
        sales_mapping = {
            "item_sold_minecraft": True,
            "prepaid_card_redeemed_minecraft": True,
            "item_sold_cobalt": False,
            "item_sold_scrolls": False,
        }
        payload = {"metricKeys": [k for (k, v) in sales_mapping.items() if v]}

        if await self.bot.redis.exists("status"):
            sales_data = json.loads(await self.bot.redis.get("status"))
        else:
            url = "https://api.mojang.com/orders/statistics"
            async with self.bot.http_session.post(
                url, json=payload, timeout=self.bot._long_http_timeout
            ) as resp:
                if resp.status == 200:
                    sales_data = await resp.json()
            await self.bot.redis.set("status", json.dumps(sales_data), px=600)

        services = ""
        for service in data:
            if data[service] == "green":
                services += _(
                    ":green_heart: - {service}: **This service is healthy.** \n"
                ).format(service=service)
            else:
                services += _(
                    ":heart: - {service}: **This service is offline.** \n"
                ).format(service=service)
        embed = discord.Embed(title=_("Minecraft Service Status"), color=0x00FF00)
        embed.add_field(
            name=_("Minecraft Game Sales"),
            value=_("Total Sales: **{total}** Last 24 Hours: **{last}**").format(
                total=sales_data["total"], last=sales_data["last24h"]
            ),
        )
        embed.add_field(name=_("Minecraft Services:"), value=services, inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="wiki",
        description="Get an article from the minecraft wiki.",
        options=[
            create_option(
                name="query",
                description="Thing to look up.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def wiki(self, ctx: SlashContext, query: str) -> None:
        def generate_payload(query: str) -> dict:
            """Generate the payload for fandom based on a query string."""
            payload = {
                "action": "query",
                "titles": query.replace(" ", "_"),
                "format": "json",
                "formatversion": "2",  # Cleaner json results
                "prop": "extracts",  # Include extract in returned results
                "exintro": "1",  # Only return summary paragraph(s) before main content
                "redirects": "1",  # Follow redirects
                "explaintext": "1",  # Make sure it's plaintext (not HTML)
            }
            return payload

        base_url = "https://minecraft.fandom.com/api.php"
        footer_icon = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53"
            "/Wikimedia-logo.png/600px-Wikimedia-logo.png"
        )

        payload = generate_payload(query)
        async with self.bot.http_session.get(base_url, params=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
            else:
                result = None

        try:
            # Get the last page. Usually this is the only page.
            page = result["query"]["pages"][-1]
            title = page["title"]
            description = page["extract"].strip().replace("\n", "\n\n")
            url = f"https://minecraft.fandom.com/{title.replace(' ', '_')}"

            if len(description) > 1500:
                description = description[:1500].strip()
                description += f"... [(read more)]({url})"

            embed = discord.Embed(
                title=title,
                description=f"\u2063\n{description}\n\u2063",
                color=self.bot.color,
                url=url,
            )
            embed.set_footer(
                text=_("Information provided by Wikimedia"), icon_url=footer_icon
            )
            await ctx.send(embed=embed)

        except KeyError:
            embed = self.bot.build_embed(
                _("Minecraft Wiki Search"),
                _("I'm sorry, I couldn't find \"{query}\" on fandom").format(
                    query=query
                ),
                "error",
            )
            await ctx.send(embed=embed, hidden=True)

    # @commands.command()
    # async def mcbug(self, ctx: Union[commands.Context, SlashContext], bug: str) -> None:
    #     """Gets info on a bug from bugs.mojang.com."""
    #     await ctx.channel.trigger_typing()
    #     await ctx.send(f"https://bugs.mojang.com/rest/api/latest/issue/{bug}")
    #     async with self.bot.http_session.get(
    #         f"https://bugs.mojang.com/rest/api/latest/issue/{bug}"
    #     ) as resp:
    #         if resp.status == 200:
    #             data = await resp.json()
    #         else:
    #             await ctx.reply(_("The bug {bug} was not found.").format(bug=bug))
    #             return
    #     embed = discord.Embed(
    #         description=data["fields"]["description"],
    #         color=self.bot.color,
    #     )

    #     embed.set_author(
    #         name=f"{data['fields']['project']['name']} - {data['fields']['summary']}",
    #         url=f"https://bugs.mojang.com/browse/{bug}",
    #     )

    #     info = _(
    #         "Version: {version}\n"
    #         "Reporter: {reporter}\n"
    #         "Created: {created}\n"
    #         "Votes: {votes}\n"
    #         "Updates: {updates}\n"
    #         "Watchers: {watched}"
    #     ).format(
    #         version=data["fields"]["project"]["name"],
    #         reporter=data["fields"]["creator"]["displayName"],
    #         created=data["fields"]["created"],
    #         votes=data["fields"]["votes"]["votes"],
    #         updates=data["fields"]["updated"],
    #         watched=data["fields"]["watches"]["watchCount"],
    #     )

    #     details = (
    #         f"Type: {data['fields']['issuetype']['name']}\n"
    #         f"Status: {data['fields']['status']['name']}\n"
    #     )
    #     if "name" in data["fields"]["resolution"]:
    #         details += _("Resolution: {resolution}\n").format(
    #             resolution=data["fields"]["resolution"]["name"]
    #         )
    #     if "version" in data["fields"]:
    #         details += (
    #             _("Affected: ")
    #             + f"{', '.join(s['name'] for s in data['fields']['versions'])}\n"
    #         )
    #     if "fixVersions" in data["fields"]:
    #         if len(data["fields"]["fixVersions"]) >= 1:
    #             details += (
    #                 _("Fixed Version: {fixed} + ").format(
    #                     fixed=data["fields"]["fixVersions"][0]
    #                 )
    #                 + f"{len(data['fields']['fixVersions'])}\n"
    #             )

    #     embed.add_field(name=_("Information"), value=info)
    #     embed.add_field(name=_("Details"), value=details)

    #     await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="version",
        description="Latest version info.",
        options=[
            create_option(
                name="version",
                description="Version to lookup.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def version(self, ctx: SlashContext, version: str = None) -> None:
        await ctx.defer()
        key = "versions"
        if await self.bot.redis.exists(key):
            data = json.loads(await self.bot.redis.get(key))
        else:
            async with self.bot.http_session.get(
                "https://launchermeta.mojang.com/mc/game/version_manifest.json",
                timeout=self.bot._long_http_timeout,
            ) as resp:
                data = await resp.json()
            await self.bot.redis.set(key, json.dumps(data), px=600)
        id2version = {}
        versions: Dict[str, Any] = {}

        for _version in reversed(data["versions"]):
            id2version[_version["id"]] = _version
            if _version["type"] == "release":
                version_num = ".".join(_version["id"].split(".")[:2])
                if version_num in versions:
                    _updated = versions[version_num]
                    _updated.append(_version)
                    versions[version_num] = _updated
                else:
                    versions[version_num] = [_version]
        embed = discord.Embed(
            colour=self.bot.color,
        )
        format = "%Y-%m-%dT%H:%M:%S%z"
        if version is not None:
            if version not in id2version:
                embed = self.bot.build_embed(
                    _("Error"),
                    _("Version {version} not found.").format(version=version),
                    "error",
                )
                await ctx.send(embed=embed)
            version_data = id2version[version]
            embed.set_author(
                name=_("Minecraft Java Edition {version}").format(version=version),
                url=f"https://minecraft.fandom.com/Java_Edition_{version}",
                icon_url=(
                    "https://www.minecraft.net/etc.clientlibs/minecraft"
                    "/clientlibs/main/resources/img/menu/menu-buy--reversed"
                    ".gif"
                ),
            )
            embed.add_field(
                name=version,
                value=_(
                    "Type: `{type}`\nRelease: `{released}`\nPackage URL: [link"
                    "]({package_url})\nMinecraft Wiki: [link]({wiki})"
                ).format(
                    type=version_data["type"],
                    released=datetime.strptime(version_data["releaseTime"], format),
                    package_url=version_data["url"],
                    wiki="https://minecraft.fandom.com/Java_Edition_{_version}",
                ),
            )
        else:
            embed.set_author(
                name=_("Minecraft Java Edition Versions"),
                icon_url=(
                    "https://www.minecraft.net/etc.clientlibs/minecraft"
                    "/clientlibs/main/resources/img/menu/menu-buy--reversed.gif"
                ),
            ),
            for _version in reversed(versions):
                embed.add_field(
                    name=_version,
                    value=_(
                        "Releases: `{releases}`\n"
                        "**Latest Version**\n"
                        "ID: `{id}`\n"
                        "Released: `{released}`\n"
                        "Wiki: [link]({link})"
                    ).format(
                        releases=len(versions[_version]),
                        id=versions[_version][-1]["id"],
                        released=datetime.strptime(
                            versions[_version][-1]["releaseTime"], format
                        ),
                        link=f"https://minecraft.fandom.com/Java_Edition_{_version}",
                    ),
                )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="news",
        description="Latest news from Mojang.",
    )
    async def news(self, ctx: SlashContext) -> None:
        data = await self.bot.get_json(
            "news",
            "https://www.minecraft.net/content/minecraft-net/_jcr_content.articles.grid?tileselection=auto",
        )
        embed = self.bot.build_embed(
            _("Latest Minecraft News"),
        )
        for post in data["article_grid"]:
            format = "%d %m %Y"
            time = datetime.strftime(
                datetime.strptime(post["publish_date"], "%d %B %Y %X %Z"),
                format,
            )
            embed.add_field(
                name=post["default_tile"]["title"],
                value=(
                    "Category: `{category}`\n"
                    "Published: `{pub}`\n"
                    "[Article Link]({link})"
                ).format(
                    category=post["primary_category"],
                    pub=time,
                    link=post["article_url"],
                ),
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="vote",
        description="Help us by voting for the bot.",
    )
    async def news(self, ctx: SlashContext) -> None:
        embed = self.bot.build_embed(
            _("Vote for the bot"),
            _("Vote for the bot on one of the voting websites."),
        )

        embed.add_field(
            name=_("Vote for the bot on Top.gg"),
            value=(
                "[Vote for the bot on Top.gg]({link})"
            ).format(
                link="https://top.gg/bot/691589447074054224/vote",
            ),
        )

        await ctx.send(embed=embed)