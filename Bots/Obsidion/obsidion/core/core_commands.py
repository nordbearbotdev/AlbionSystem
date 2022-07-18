"""Core Commands."""
from __future__ import annotations

import datetime
import inspect
import logging
import os
import sys
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from obsidion import __version__
from obsidion.core.config import get_settings
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator

from .utils.chat_formatting import humanize_timedelta

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion


log = logging.getLogger("obsidion")

_ = Translator("Core", __file__)


@cog_i18n(_)
class Core(commands.Cog):
    """Commands related to core functions."""

    def __init__(self, bot: Obsidion) -> None:
        """Init Core Commands."""
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="View bot latency.")
    async def ping(self, ctx: SlashContext) -> None:
        """View bot latency."""
        await ctx.send(_("Pong! ({latency}ms)").format(latency=self.bot.latency * 1000))

    @cog_ext.cog_slash(name="info", description="View info about the bot.")
    async def info(self, ctx: SlashContext) -> None:
        """Shows info about Obsidion."""
        author_repo = "https://github.com/Darkflame72"
        org_repo = "https://github.com/Obsidion-dev"
        obsidion_repo = org_repo + "/Obsidion"
        support_server_url = "https://discord.gg/fWxtKFVmaW"
        dpy_repo = "https://github.com/Rapptz/discord.py"
        python_url = "https://www.python.org/"
        since = datetime.datetime(2020, 4, 2)
        days_since = (datetime.datetime.utcnow() - since).days

        app_info = await self.bot.application_info()
        if app_info.team:
            owner = app_info.team.name
        else:
            owner = app_info.owner

        dpy_version = "[{}]({})".format(discord.__version__, dpy_repo)
        python_version = "[{}.{}.{}]({})".format(*sys.version_info[:3], python_url)
        obsidion_version = "[{}]({})".format(__version__, obsidion_repo)

        about = _(
            "This bot is an instance of [Obsidion, an open source Discord bot]({}) "
            "created by [Darkflame72]({}) and [improved by many]({}).\n\n"
            "Obsidion is backed by a passionate community who contributes and "
            "creates content for everyone to enjoy. [Join us today]({}) "
            "and help us improve!\n\n"
            "(c) Obsidion-dev"
        ).format(obsidion_repo, author_repo, org_repo, support_server_url)

        embed = self.bot.build_embed(
            title=_("About Obsidion"),
            description=about,
            type="info",
        )
        embed.add_field(name=_("Instance owned by"), value=str(owner))
        embed.add_field(name=_("Python"), value=python_version)
        embed.add_field(name=_("discord.py"), value=dpy_version)
        embed.add_field(name=_("Obsidion version"), value=obsidion_version)
        embed.add_field(name=_("Server Name"), value=get_settings().SERVER_NAME)

        embed.set_footer(text=_("Bringing joy for over {} days!").format(days_since))
        embed.timestamp = since
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="uptime", description="View Obsidion's uptime.")
    async def uptime(self, ctx: SlashContext) -> None:
        """Shows Obsidion's uptime."""
        since = self.bot.uptime.strftime("%Y-%m-%d %H:%M:%S")
        delta = datetime.datetime.utcnow() - self.bot.uptime
        uptime_str = humanize_timedelta(timedelta=delta) or _("Less than one second")
        embed = self.bot.build_embed(
            title=_("Uptime"),
            description=_("Uptime: {}").format(uptime_str),
            type="info",
        )
        embed.add_field(name=_("Since"), value=since)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="invite", description="Invite the bot to your server.")
    async def invite(self, ctx: SlashContext) -> None:
        """Invite the bot to your server."""
        embed = self.bot.build_embed(
            _("Invite"),
            _(
                "You can invite {name} to your Discord server by"
                " [clicking here]({invite}).\nIf you want it to do server"
                " tracking or news posting invite it as a bot [here]({invite_bot})."
            ).format(
                name=self.bot.user.name,
                invite=self.bot._invite,
                invite_bot=self.bot._invite_bot,
            ),
            "info",
        )
        await ctx.send(embed=embed)

    # Removing this command from forks is a violation of the
    # AGPLv3 under which it is licensed.
    # Otherwise interfering with the ability for this command
    # to be accessible is also a violation.
    @cog_ext.cog_slash(
        name="licenseinfo", description="View info about the bot's license."
    )
    async def licenseinfo(self, ctx: SlashContext) -> None:
        """Leaves the current server."""
        embed = self.bot.build_embed(
            _("License Info"),
            _(
                "This bot is an instance of the Obsidion Discord Bot.\n"
                "Obsidion is an open source application made available "
                "to the public and "
                "licensed under the GNU AGPL v3. The full text of this "
                "license is available to you at "
                "<https://github.com/Obsidion-dev/Obsidion/blob/main/LICENSE>"
            ),
            "info",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="source",
        description="Displays my full source code or for a specific command.",
        options=[
            create_option(
                name="command",
                description="Command to view source of.",
                option_type=3,
                required=False,
            )
        ],
    )
    async def source(self, ctx: SlashContext, command: str = None) -> None:
        """Displays my full source code or for a specific command."""
        source_url = "https://github.com/Obsidion-dev/Obsidion"
        branch = "main"
        filename: str
        if command is None:
            await ctx.send(source_url)
            return
        elif command == "help":
            src = type(self.bot.help_command)
            module = src.__module__
            filename = str(inspect.getsourcefile(src))
        else:
            obj = self.bot.get_command(command.replace(".", " "))
            if obj is None:
                await ctx.send(_("Could not find command."), hidden=True)
            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            # not a built-in command
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/Rapptz/discord.py"
            branch = "main"

        final_url = (
            f"<{source_url}/blob/{branch}/{location}#L{firstlineno}"
            f"-L{firstlineno + len(lines) - 1}>"
        )
        await ctx.send(final_url)
