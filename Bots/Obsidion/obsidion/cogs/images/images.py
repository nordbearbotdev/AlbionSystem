"""Images cog."""
from __future__ import annotations

import logging
from typing import Optional
from typing import TYPE_CHECKING
from urllib.parse import quote

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option
from obsidion.core import get_settings
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion


log = logging.getLogger(__name__)

_ = Translator("Images", __file__)


@cog_i18n(_)
class Images(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot

    @cog_ext.cog_slash(
        name="achievement",
        description="Create your very own custom Minecraft achievements.",
        options=[
            create_option(
                name="name",
                description="Minecraft item name",
                option_type=3,
                required=True,
            ),
            create_option(
                name="title",
                description="Title of the achievement",
                option_type=3,
                required=True,
            ),
            create_option(
                name="text",
                description="Text of the achievement.",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def achievement(
        self,
        ctx: SlashContext,
        name: str,
        title: str,
        text: str,
    ) -> None:
        text = text.replace(" ", "%20")
        async with self.bot.http_session.get(
            f"{get_settings().API_URL}/images/advancement?item={name}&tit"
            f"le={title}&text={text}"
        ) as resp:
            if resp.status == 500:
                await ctx.send(_("That item is not available."))
                return
        embed = self.bot.build_embed(
            title=_("Achievement created!"),
        )
        embed.set_image(
            url=(
                f"{get_settings().API_URL}/images/advancement?item={name}"
                f"&title={quote(title)}&text={quote(text)}"
            )
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="sign",
        description="Render a Minecraft Sign.",
        options=[
            create_option(
                name="line1",
                description="Text to go on line 1.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="line2",
                description="Text to go on line 2.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="line3",
                description="Text to go on line 3.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="line4",
                description="Text to go on line 4.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def sign(
        self,
        ctx: SlashContext,
        line1: str,
        line2: str = "%20",
        line3: str = "%20",
        line4: str = "%20",
    ) -> None:
        embed = self.bot.build_embed(
            title=_("Sign created!"),
        )
        embed.set_image(
            url=(
                f"{get_settings().API_URL}/images/sign?line1={quote(line1)}"
                f"&line2={quote(line2)}&line3={quote(line3)}&line4={quote(line4)}"
            )
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="avatar",
        description="Renders a Minecraft players face.",
        options=[
            create_option(
                name="username",
                description="Username of account defaults to linked account.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def avatar(self, ctx: SlashContext, username: str = None) -> None:
        embed = await self.build_render(ctx.author, ctx.guild, "face", username)
        if isinstance(embed, str):
            await ctx.send(embed)
        else:
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="skull",
        description="Renders a Minecraft players skull.",
        options=[
            create_option(
                name="username",
                description="Username of account defaults to linked account.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def skull(self, ctx: SlashContext, username: str = None) -> None:
        embed = await self.build_render(ctx.author, ctx.guild, "head", username)
        if isinstance(embed, str):
            await ctx.send(embed)
        else:
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="skin",
        description="Renders a Minecraft players skin.",
        options=[
            create_option(
                name="username",
                description="Username of account defaults to linked account.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def skin(self, ctx: SlashContext, username: str = None) -> None:
        embed = await self.build_render(ctx.author, ctx.guild, "full", username)
        if isinstance(embed, str):
            await ctx.send(embed)
        else:
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="bust",
        description="Renders a Minecraft players bust.",
        options=[
            create_option(
                name="username",
                description="Username of account defaults to linked account.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def bust(self, ctx: SlashContext, username: str = None) -> None:
        embed = await self.build_render(ctx.author, ctx.guild, "bust", username)
        if isinstance(embed, str):
            await ctx.send(embed)
        else:
            await ctx.send(embed=embed)

    async def build_render(
        self,
        author: discord.User,
        guild: discord.Guild,
        render_type: str,
        username: Optional[str] = None,
    ):
        renders = ["face", "front", "frontfull", "head", "bust", "full", "skin"]
        if render_type not in renders:
            return _(
                "Please supply a render type. Your "
                "options are:\n `face`, `front`, `full`, `head`, `bust`, "
                "`skin` \n Type: {prefix}render <render type> <username>"
            ).format(prefix=(await self.bot._prefix_cache.get_prefixes(guild))[0])
        player_data = await self.bot.mojang_player(author, username)
        uuid = player_data["uuid"]
        username = player_data["username"]
        embed = self.bot.build_embed(
            title=_("Render of {username}'s {render_type}").format(
                username=username, render_type=render_type.capitalize()
            ),
            description=_(
                "**[DOWNLOAD](https://visage.surgeplay.com/{render_type_lower}/512/"
                "{uuid})\n[RAW](https://visage.surgeplay.com/skin/512/{uuid})**"
            ).format(render_type_lower=render_type, uuid=uuid),
        )
        embed.set_image(url=f"https://visage.surgeplay.com/{render_type}/512/{uuid}")
        return embed

    @cog_ext.cog_slash(
        name="render",
        description="Renders a Minecraft players skin in 6 different ways.",
        options=[
            create_option(
                name="render_type",
                description="Type of render.",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Face", value="face"),
                    create_choice(name="Front 2d", value="front"),
                    create_choice(name="Full", value="full"),
                    create_choice(name="Head", value="head"),
                    create_choice(name="Bust", value="bust"),
                    create_choice(name="Skin", value="skin"),
                ],
            ),
            create_option(
                name="username",
                description="Username of account defaults to linked account.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def render(
        self, ctx: SlashContext, render_type: str, username: str = None
    ) -> None:
        embed = await self.build_render(ctx.author, ctx.guild, render_type, username)
        if isinstance(embed, str):
            await ctx.send(embed)
        else:
            await ctx.send(embed=embed)
