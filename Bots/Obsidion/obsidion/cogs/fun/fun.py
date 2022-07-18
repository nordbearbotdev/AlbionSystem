"""Fun cog."""
from __future__ import annotations

import logging
from random import choice
from typing import List
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion


log = logging.getLogger(__name__)

_ = Translator("Fun", __file__)

minecraft = (
    "ᔑ",
    "ʖ",
    "ᓵ",
    "↸",
    "ᒷ",
    "⎓",
    "⊣",
    "⍑",
    "╎",
    "⋮",
    "ꖌ",
    "ꖎ",
    "ᒲ",
    "リ",
    "𝙹",
    "!¡",
    "ᑑ",
    "∷",
    "ᓭ",
    "ℸ",
    "⚍",
    "⍊",
    "∴",
    " ̇",
    "||",
    "⨅",
)
alphabet = "abcdefghijklmnopqrstuvwxyz"


@cog_i18n(_)
class Fun(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot
        self.pvp_mes = self.load_from_file("pvp")
        self.kill_mes = self.load_from_file("kill")
        self.build_ideas_mes = self.load_from_file("build_ideas")

    @staticmethod
    def load_from_file(file: str) -> List[str]:
        """Load text from file.
        Args:
            file (str): file name
        Returns:
            List[str]: list of input
        """
        with open(f"obsidion/cogs/fun/resources/{file}.txt") as f:
            content = f.readlines()
        return [x.strip() for x in content]

    @cog_ext.cog_slash(name="buildidea", description="Get an idea for a new build.")
    async def buildidea(self, ctx: SlashContext) -> None:
        """Get an idea for a new build."""
        embed = self.bot.build_embed(
            title=_("Build idea"),
            description=choice(self.build_ideas_mes),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="kill",
        description="Kill that pesky friend in a fun and stylish way.",
        options=[
            create_option(
                name="username", description="Friend.", option_type=6, required=True
            )
        ],
    )
    async def kill(self, ctx: SlashContext, username: discord.Member) -> None:
        """Get an idea for a new build."""
        embed = self.bot.build_embed(
            title=_("Kill"),
            description=choice(self.kill_mes).replace("member", username.mention),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="pvp",
        description="Duel someone.",
        options=[
            create_option(
                name="player1", description="Player 1.", option_type=6, required=True
            ),
            create_option(
                name="player2", description="Player 2.", option_type=6, required=False
            ),
        ],
    )
    async def pvp(
        self, ctx: SlashContext, player1: discord.Member, player2: discord.Member = None
    ) -> None:
        """Get an idea for a new build."""
        if not player2:
            player2 = ctx.author
        embed = self.bot.build_embed(
            title=_("PVP"),
            description=choice(self.pvp_mes)
            .replace("member1", player1.mention)
            .replace("member2", player2.mention),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="villager",
        description="Hmm hm hmmm Hm hmmm hmm.",
        options=[
            create_option(
                name="speech",
                description="Hmm",
                option_type=3,
                required=True,
            )
        ],
    )
    async def villager(self, ctx: SlashContext, speech: str):
        last_was_alpha = False  # Used to detect the start of a word
        last_was_h = False  # Used to prevent 'H's without 'm's
        last_was_lower_m = False  # Used to make "HmmHmm" instead of "HmmMmm"
        sentence = ""

        for char in speech:

            if char.isalpha():  # Alphabetical letter -- Replace with 'Hmm'

                if not last_was_alpha:  # First letter of alphabetical string
                    sentence += "H" if char.isupper() else "h"
                    last_was_h = True
                    last_was_lower_m = False

                else:  # Non-first letter
                    if not char.isupper():
                        sentence += "m"
                        last_was_lower_m = True
                        last_was_h = False
                    else:
                        # Use an 'H' instead to allow CamelCase 'HmmHmm's
                        if last_was_lower_m:
                            sentence += "H"
                            last_was_h = True
                        else:
                            sentence += "M"
                            last_was_h = False
                        last_was_lower_m = False

                last_was_alpha = True  # Remember for next potential 'M'

            else:  # Non-alphabetical letters -- Do not replace
                # Add an m after 'H's without 'm's
                if last_was_h:
                    sentence += "m"
                    last_was_h = False
                # Add non-letter character without changing it
                sentence += char
                last_was_alpha = False

        # If the laster character is an H, add a final 'm'
        if last_was_h:
            sentence += "m"
        await ctx.send(speech)

    @cog_ext.cog_slash(
        name="enchant",
        description="Enchant a message.",
        options=[
            create_option(
                name="msg",
                description="Text to enchant or unenchant.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def enchant(self, ctx, msg: str):
        response = ""
        letter_pos = 0
        while letter_pos < len(msg):
            letter = (
                msg[letter_pos : letter_pos + 2]
                if msg[letter_pos : letter_pos + 2] in minecraft
                else msg[letter_pos]
            )
            letter = letter.lower()
            if letter in alphabet:
                response += minecraft[alphabet.index(letter)]
            elif letter in minecraft:
                response += alphabet[minecraft.index(letter)]
                if len(letter) == 2:
                    letter_pos += 1
            else:
                response += letter
            letter_pos += 1
        embed = self.bot.build_embed(
            title=_("Enchant"),
            description=response,
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="creeper", description="Aw man.")
    async def creeper(self, ctx: SlashContext):
        """Aw man."""
        await ctx.send("Aw man.")

    @cog_ext.cog_slash(
        name="rps",
        description="Play Rock Paper Shears.",
        options=[
            create_option(
                name="choice",
                description="Rock paper or shears",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Rock", value="rock"),
                    create_choice(name="Paper", value="paper"),
                    create_choice(name="Shears", value="shears"),
                ],
            )
        ],
    )
    async def rps(self, ctx: SlashContext, user_choice: str):
        """Play Rock Paper Shears"""
        options = ["rock", "paper", "shears"]
        c_choice = choice(options)
        if user_choice == options[options.index(user_choice) - 1]:
            msg = _("You chose {user_choice}, I chose {c_choice} I win.").format(
                user_choice=user_choice, c_choice=c_choice
            )
        elif c_choice == user_choice:
            msg = _(
                "You chose {user_choice}, I chose {c_choice} looks like we"
                " have a tie."
            ).format(user_choice=user_choice, c_choice=c_choice)
        else:
            msg = _("You chose {user_choice}, I chose {c_choice} you win.").format(
                user_choice=user_choice, c_choice=c_choice
            )
        embed = self.bot.build_embed(title=_("Rock Paper Shears"), description=msg)
        await ctx.send(embed=embed)
