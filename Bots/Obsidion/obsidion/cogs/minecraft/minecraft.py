"""Minecraft cog."""
from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion

log = logging.getLogger(__name__)

_ = Translator("Minecraft", __file__)


@cog_i18n(_)
class Minecraft(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="convert",
        name="second",
        description="Convert ticks to seconds.",
        options=[
            create_option(
                name="ticks",
                description="Ticks.",
                option_type=4,
                required=True,
            )
        ],
    )
    async def second(self, ctx: SlashContext, ticks: int) -> None:
        if ticks <= 0:
            embed = self.bot.build_embed(
                title=_("Invalid Input"),
                description=_("Input must be greater than 0."),
                type="error",
            )
            await ctx.send(embed=embed, hidden=True)
            return
        try:
            seconds = ticks / 20
        except OverflowError:
            embed = self.bot.build_embed(
                title=_("Invalid Input"),
                description=_("Ticks must be greater than 0."),
                type="error",
            )
            await ctx.send(embed=embed, hidden=True)
            return

        embed = self.bot.build_embed(
            _("Seconds to Tick Conversion"),
            _("It takes `{seconds}` seconds for `{ticks}` ticks to happen.").format(
                seconds=seconds, ticks=ticks
            ),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="convert",
        name="tick",
        description="Convert seconds to ticks.",
        options=[
            create_option(
                name="seconds",
                description="Seconds.",
                option_type=10,
                required=True,
            )
        ],
    )
    async def tick(self, ctx: SlashContext, seconds: int) -> None:
        if seconds <= 0:
            embed = self.bot.build_embed(
                title=_("Invalid Input"),
                description=_("Input must be greater than 0."),
                type="error",
            )
            await ctx.send(embed=embed, hidden=True)
            return
        ticks = seconds * 20
        embed = self.bot.build_embed(
            _("Ticks to Seconds Conversion"),
            _("There are `{ticks}` ticks in `{seconds}` seconds").format(
                ticks=ticks, seconds=seconds
            ),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="convert",
        name="chest",
        description=(
            "The output of a comparator based on"
            " the number of items in a single chest."
        ),
        options=[
            create_option(
                name="items",
                description="Number of items in the chest.",
                option_type=4,
                required=True,
            )
        ],
    )
    async def chest(self, ctx: SlashContext, items: int) -> None:
        fullness = math.floor(1 + ((items / 64) / (27)) * 14)
        if fullness == 0:
            embed = self.bot.build_embed(
                title=_("Invalid Input"),
                description=_("Input must be greater than 0."),
                type="error",
            )
            await ctx.send(embed=embed, hidden=True)
            return
        embed = self.bot.build_embed(
            _("Chest Comparator"),
            _(
                "The chest will output a redstone signal of strength: `{fullness}`."
            ).format(fullness=fullness),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="convert",
        name="comparator",
        description="Items in a chest based on comparator strength.",
        options=[
            create_option(
                name="strength",
                description="Strength of redstone output.",
                option_type=4,
                required=True,
            )
        ],
    )
    async def comparator(self, ctx: SlashContext, strength: int) -> None:
        if strength < 0 or strength > 15:
            embed = self.bot.build_embed(
                title=_("Invalid Input"),
                description=_("Input must be between 0 and 15."),
                type="error",
            )
            return
        items = max(strength, math.ceil((27 * 64 / 14) * (strength - 1)))
        embed = self.bot.build_embed(
            _("Chest Comparator"),
            _("The chest is `{strength}%` full. It is holding `{items}` items.").format(
                strength=(strength / 15 * 100), items=items
            ),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="seed",
        description="Convert text to minecraft numerical seed.",
        options=[
            create_option(
                name="text",
                description="Seed in text format to see numerical representation",
                option_type=3,
                required=True,
            )
        ],
    )
    async def seed(self, ctx: SlashContext, text: str) -> None:
        try:
            seed = str(int(text))
        except ValueError:
            h = 0
            for c in text:
                h = (31 * h + ord(c)) & 0xFFFFFFFF
            seed = str(((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000)
        embed = self.bot.build_embed(
            _("Seed"),
            _("The seed for {text} is: `{seed}`").format(text=text, seed=seed),
        )
        await ctx.send(embed=embed)
