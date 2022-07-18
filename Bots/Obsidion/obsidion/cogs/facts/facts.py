"""Facts cog."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from obsidion.core.errors import NotFoundError
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion

log = logging.getLogger(__name__)

_ = Translator("Facts", __file__)


@cog_i18n(_)
class Facts(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot

    async def get_from_api(self, name: str, version: str, _type: str):
        name = name.replace(" ", "_").lower()
        params = {"name_id": name, "version": version}
        key = f"{_type}_{name}_version"
        endpoint = f"info/{_type}"
        data = await self.bot.get_api_json(key, endpoint, params)
        if data is None:
            raise NotFoundError(_type, name)
        return (data, name)

    def build_embed(self, name: str, display_name: str) -> discord.Embed:
        embed = self.bot.build_embed(display_name)
        embed.set_author(name=display_name, url=f"https://minecraft.fandom.com/{name}")
        return embed

    @cog_ext.cog_slash(
        name="block",
        description="Info about a Minecraft block.",
        options=[
            create_option(
                name="name",
                description="Name of block.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="version",
                description="Minecraft version (defaults to latest).",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def block(
        self, ctx: SlashContext, name: str, version: str = "1.16.5"
    ) -> None:
        data, name = await self.get_from_api(name, version, "block")
        embed = self.build_embed(name, data["displayName"])
        embed.add_field(name=_("Display Name"), value=data["displayName"])
        embed.add_field(name=_("ID"), value=data["id"])
        embed.add_field(name=_("Stack Size"), value=data["stackSize"])
        embed.add_field(name=_("hardness"), value=data["hardness"])
        embed.add_field(name=_("diggable"), value=data["diggable"])
        embed.add_field(name=_("transparent"), value=data["transparent"])
        embed.add_field(name=_("filterLight"), value=data["filterLight"])
        embed.add_field(name=_("emitLight"), value=data["emitLight"])
        if "material" in data:
            embed.add_field(name=_("material"), value=data["material"])
        embed.add_field(name=_("resistance"), value=data["resistance"])
        if "harvestTools" in data:
            embed.add_field(
                name=_("harvestTools"), value="\n".join(data["harvestTools"])
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="entity",
        description="Info about a Minecraft entity.",
        options=[
            create_option(
                name="name",
                description="Name of entity.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="version",
                description="Minecraft version.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def entity(
        self, ctx: SlashContext, name: str, version: str = "1.16.5"
    ) -> None:
        data, name = await self.get_from_api(name, version, "entity")
        embed = self.build_embed(name, data["displayName"])
        embed.add_field(name=_("Display Name"), value=data["displayName"])
        embed.add_field(name=_("ID"), value=data["id"])
        embed.add_field(name=_("width"), value=data["width"])
        embed.add_field(name=_("height"), value=data["height"])
        embed.add_field(name=_("type"), value=data["type"])
        embed.add_field(name=_("category"), value=data["category"])
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="biome",
        description="Info about a Minecaft biome.",
        options=[
            create_option(
                name="name",
                description="Name of biome.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="version",
                description="Minecraft version.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def biome(
        self, ctx: SlashContext, name: str, version: str = "1.16.5"
    ) -> None:
        data, name = await self.get_from_api(name, version, "biome")

        def getrgbfromi(rgbint):
            blue = rgbint & 255
            green = (rgbint >> 8) & 255
            red = (rgbint >> 16) & 255
            return red, green, blue

        colour = getrgbfromi(data["color"])
        embed = self.build_embed(data["displayName"], data["displayName"])
        embed.color = discord.Colour.from_rgb(colour[0], colour[1], colour[2])
        embed.add_field(name=_("Display Name"), value=data["displayName"])
        embed.add_field(name=_("Category"), value=data["category"])
        embed.add_field(name=_("Dimension"), value=data["dimension"])
        embed.add_field(name=_("ID"), value=data["id"])
        embed.add_field(name=_("Temperature"), value=data["temperature"])
        embed.add_field(name=_("Colour"), value="#%02x%02x%02x" % tuple(colour))
        embed.add_field(name=_("Rainfall"), value=data["rainfall"])
        embed.add_field(name=_("Precipitation"), value=data["precipitation"])
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="effect",
        description="Info about a Minecaft effect.",
        options=[
            create_option(
                name="name",
                description="Name of effect.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="version",
                description="Minecraft version.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def effect(
        self, ctx: SlashContext, name: str, version: str = "1.16.5"
    ) -> None:
        data, name = await self.get_from_api(name, version, "effect")

        embed = self.build_embed(name, data["displayName"])
        embed.add_field(name=_("Display Name"), value=data["displayName"])
        embed.add_field(name=_("ID"), value=data["id"])
        embed.add_field(name=_("type"), value=data["type"])
        await ctx.send(embed=embed)
