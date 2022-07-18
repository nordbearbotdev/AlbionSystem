from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import discord
from discord.ext import commands
from discord_slash.context import SlashContext

from .errors import NotFoundError
from .errors import PlayerNotExistError
from .errors import ProvideServerError
from .errors import ServerUnavailableError
from .i18n import cog_i18n
from .i18n import set_contextual_locales_from_guild
from .i18n import Translator
from .utils.chat_formatting import format_perms_list
from .utils.chat_formatting import humanize_timedelta


if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion


log = logging.getLogger("obsidion")

_ = Translator("Events", __file__)


@cog_i18n(_)
class Events(commands.Cog):
    """Important bot events."""

    def __init__(self, bot: Obsidion):
        self.bot = bot

    @commands.Cog.listener("on_connect")
    async def on_connect(self):
        if self.bot.uptime is None:
            log.info("Connected to Discord. Getting ready...")
            perms = discord.Permissions()
            perms.send_messages = True
            perms.embed_links = True
            url = discord.utils.oauth_url(
                self.bot.user.id,
                permissions=perms,
                redirect_uri="https://discord.obsidion-dev.com",
                scopes=("bot", "applications.commands"),
            )
            url_bot = discord.utils.oauth_url(
                self.bot.user.id,
                redirect_uri="https://discord.obsidion-dev.com",
                scopes=("applications.commands",),
            )
            self.bot._invite_bot = url_bot
            self.bot._invite = url

    @commands.Cog.listener()
    async def on_message(self, message):
        await set_contextual_locales_from_guild(self.bot, message.guild)

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        if self.bot.uptime is not None:
            return

        self.bot.uptime = datetime.utcnow()
        log.info("Connected to Discord. Getting ready...")
        perms = discord.Permissions()
        perms.send_messages = True
        perms.embed_links = True
        url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=perms,
            redirect_uri="https://discord.obsidion-dev.com",
            scopes=("bot", "applications.commands"),
        )
        url_bot = discord.utils.oauth_url(
            self.bot.user.id,
            redirect_uri="https://discord.obsidion-dev.com",
            scopes=("applications.commands",),
        )
        self.bot._invite_bot = url_bot
        self.bot._invite = url

    @staticmethod
    async def handle(
        ctx,
        embed: Optional[discord.Embed] = None,
        text: Optional[str] = None,
    ):
        if embed is not None:
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(text, hidden=True)

    @commands.Cog.listener("on_slash_command_error")
    async def on_slash_command_error(self, ctx: SlashContext, ex) -> None:
        await self.on_command_error(ctx, ex)

    async def handle_check_failure(self, ctx: commands.Context, e) -> None:
        """
        Send an error message in `ctx` for certain types of CheckFailure.
        The following types are handled:
        * BotMissingPermissions
        * BotMissingRole
        * BotMissingAnyRole
        * NoPrivateMessage
        * InWhitelistCheckFailure
        """
        bot_missing_errors = (
            commands.errors.MissingPermissions,
            commands.errors.MissingRole,
            commands.errors.MissingAnyRole,
        )

        if isinstance(e, bot_missing_errors):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in e.missing_perms
            ]
            if len(missing) > 2:
                fmt = f"{'**, **'.join(missing[:-1])}, and {missing[-1]}"
            else:
                fmt = " and ".join(missing)
            if len(missing) > 1:
                msg = _(
                    "Sorry, it looks like you don't have the **{fmt}** perm"
                    "missions I need to do that."
                ).format(fmt=fmt)
            else:
                msg = _(
                    "Sorry, it looks like you don't have the **{fmt}** per"
                    "missions I need to do that."
                ).format(fmt=fmt)
            # send as text incase of embeds
            await self.handle(ctx, text=msg)

    async def max_concurrency(self, ctx: commands.Context, error) -> None:
        if error.per is commands.BucketType.default:
            if error.number > 1:
                msg = _(
                    "Too many people using this command."
                    " It can only be used {number} times concurrently."
                ).format(number=error.number)
            else:
                msg = _(
                    "Too many people using this command."
                    " It can only be used once concurrently."
                )
        elif error.per in (commands.BucketType.user, commands.BucketType.member):
            if error.number > 1:
                msg = _(
                    "That command is still completing,"
                    " it can only be used {number} times per {type} concurrently."
                ).format(number=error.number, type=error.per.name)
            else:
                msg = _(
                    "That command is still completing,"
                    " it can only be used once per {type} concurrently."
                ).format(type=error.per.name)
        else:
            if error.number > 1:
                msg = _(
                    "Too many people using this command."
                    " It can only be used {number} times per {type} concurrently."
                ).format(number=error.number, type=error.per.name)
            else:
                msg = _(
                    "Too many people using this command."
                    " It can only be used once per {type} concurrently."
                ).format(type=error.per.name)

        embed = self.bot.build_embed(
            title=_("This command is too popular!"), description=msg, type="error"
        )
        await self.handle(ctx, embed=embed)

    async def send_traceback(self, ctx: commands.Context, error) -> None:
        if hasattr(ctx.command, "qualified_name"):
            name = ctx.command.qualified_name
        else:
            name = ctx.name
        log.exception(
            "Exception in slash command '{}'".format(name),
            exc_info=error,
        )

        message = _(
            "Error in command '{command}'. It has "
            "been recorded and should be fixed soon."
        ).format(command=name)
        exception_log = "Exception in command '{}'\n" "".format(name)
        exception_log += "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        embed = self.bot.build_embed(
            title=_("Whoops, looks like I had an error!"),
            description=message,
            type="error",
        )
        await self.handle(ctx, embed=embed)

    async def command_invoke(self, ctx: SlashContext, error) -> None:
        if (
            isinstance(error.__cause__, discord.errors.HTTPException)
            or type(error) == discord.errors.HTTPException
        ):
            if (
                hasattr(error, "code")
                and error.code == 50035
                or hasattr(error, "original")
                and error.original.code == 50035
            ):
                embed = self.bot.build_embed(
                    title=_("Invalid input!"),
                    description=_(
                        "The input you provided is too long! Please provide "
                        "an input with less then 2000 characters so that"
                        "discord will let me reply."
                    ),
                    type="error",
                )
                await self.handle(ctx, embed=embed)
                return
        elif type(error) == PlayerNotExistError:
            username = error.username
            if username is None:
                title = _("No username provided!")
                description = _(
                    "You haven't provided a username! Either specify a "
                    "username, or link your account so you don't have to type "
                    "your username every time! /account link"
                )
            else:
                title = _("Invalid Username!")
                description = _(
                    "The username you provided, `{username}`, is not a valid "
                    "username!\n\n"
                    "Click [here]({link}) if you'd like to search NameMC."
                ).format(
                    username=username, link=f"https://namemc.com/search?q={username}"
                )
            embed = self.bot.build_embed(
                title=title, description=description, type="error"
            )
            await self.handle(ctx, embed=embed)
            return

        elif type(error) == ServerUnavailableError:
            embed = self.bot.build_embed(
                title=_("Server Unavailable!").format(name=error.name),
                description=_(
                    "The server `{name}` is currently offline or "
                    "not responding. Please check that you provided "
                    "the correct address and port or try again later."
                ).format(name=error.name),
                type="error",
            )
            await self.handle(ctx, embed=embed)
            return
        if type(error) == ProvideServerError:
            embed = self.bot.build_embed(
                title=_("No server provided!"),
                description=_(
                    "You haven't provided a server! Either specify a "
                    "server, or link your Minecraft server to your "
                    "Discord server so you don't have to type your server "
                    "every time! /serverlink link [minecraft server]"
                ),
                type="error",
            )
            await self.handle(ctx, embed=embed)
            return

        elif type(error) == NotFoundError:
            embed = self.bot.build_embed(
                title=_("Could not find {name}!").format(name=error.name),
                description=_(
                    "The {name} `{search}` could not be found, please "
                    "check it is spelt correctly."
                ).format(name=error.name, search=error.search),
                type="error",
            )
            await self.handle(ctx, embed=embed)
            return

        elif (
            isinstance(error.__cause__, asyncio.TimeoutError)
            or type(error) == asyncio.TimeoutError
        ):
            title = _("API timeout!")
            description = _(
                "Looks like the api we use cannot be reached, please try again later."
            )
            embed = self.bot.build_embed(
                title=title, description=description, type="error"
            )
            await self.handle(ctx, embed=embed)
            return

        await self.send_traceback(ctx, error)

    @commands.Cog.listener("on_command_error")
    async def on_command_error(
        self,
        ctx: SlashContext,
        error: Union[discord.DiscordExceptionCommandError],
        unhandled_by_cog: bool = False,
    ):
        if not unhandled_by_cog:
            if hasattr(ctx.command, "on_error"):
                return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.CommandNotFound):
            # ignore error
            pass
        elif isinstance(error, commands.ArgumentParsingError):
            msg = _("`{user_input}` is not a valid value for `{command}`").format(
                user_input=error.user_input, command=error.cmd
            )
            if error.custom_help_msg:
                msg += f"\n{error.custom_help_msg}"
            embed = self.bot.build_embed(
                title=_("Command Argument error!"), description=msg, type="error"
            )
            await self.handle(ctx, embed=embed)
            if error.send_cmd_help:
                await ctx.send_help(ctx.command)
        elif isinstance(error, commands.ConversionError):
            if error.args:
                await self.handle(ctx, text=error.args[0])
            else:
                await ctx.send_help(ctx.command)
        elif isinstance(error, commands.UserInputError):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.BotMissingPermissions):
            if bin(error.missing.value).count("1") == 1:  # Only one perm missing
                msg = _(
                    "I require the {permission} permission to execute that command."
                ).format(permission=format_perms_list(error.missing))
            else:
                msg = _(
                    "I require {permission_list} permissions to execute that command."
                ).format(permission_list=format_perms_list(error.missing))
            embed = self.bot.build_embed(
                title=_("Bot permissions missing!"), description=msg, type="error"
            )
            await self.handle(ctx, embed=embed)
        elif isinstance(error, commands.NoPrivateMessage):
            await self.handle(ctx, text=("That command is not available in DMs."))
        elif isinstance(error, commands.PrivateMessageOnly):
            await self.handle(ctx, text=("That command is only available in DMs."))
        elif isinstance(error, commands.CheckFailure):
            await self.handle_check_failure(ctx, error)
        elif isinstance(error, commands.CommandOnCooldown):
            if delay := humanize_timedelta(seconds=error.retry_after):
                msg = _("This command is on cooldown. Try again in {delay}.").format(
                    delay=delay
                )
            else:
                msg = _("This command is on cooldown. Try again in 1 second.")
            await ctx.send(msg, delete_after=error.retry_after)
        elif isinstance(error, commands.MaxConcurrencyReached):
            await self.max_concurrency(ctx, error)
        elif isinstance(error, commands.CommandInvokeError) or ctx.channel:
            await self.command_invoke(ctx, error)
        else:
            log.exception(type(error).__name__, exc_info=error)
