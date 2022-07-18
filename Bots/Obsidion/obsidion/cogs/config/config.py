"""Config cog."""
from __future__ import annotations

import logging
from typing import Optional
from typing import TYPE_CHECKING

import discord
from babel import Locale as BabelLocale
from babel import UnknownLocaleError
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from obsidion.core import i18n
from obsidion.core.i18n import cog_i18n
from obsidion.core.i18n import Translator
from obsidion.core.settings_cache import NewsType

if TYPE_CHECKING:
    from obsidion.core.bot import Obsidion


log = logging.getLogger(__name__)

_ = Translator("Config", __file__)


@cog_i18n(_)
class Config(commands.Cog):
    def __init__(self, bot: Obsidion) -> None:
        """Init."""
        self.bot = bot

    @cog_ext.cog_slash(
        name="locale",
        description="Changes the bot's locale in this server.",
        options=[
            create_option(
                "language_code",
                "can be any language code with country code included, e.g. `en-US`, `de-DE`, `fr-FR`, `pl-PL`, etc.",
                3,
                True,
            )
        ],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def locale(self, ctx: SlashContext, language_code: str):
        """
        Changes the bot's locale in this server.

        `<language_code>` can be any language code with country code included,
        e.g. `en-US`, `de-DE`, `fr-FR`, `pl-PL`, etc.


        Use "default" to return to the bot's default set language.
        To reset to English, use "en-US".
        """
        title = _("Changing locale")
        if language_code.lower() == "default":
            global_locale = await self.bot._config.locale()
            i18n.set_contextual_locale(global_locale)
            await self.bot._i18n_cache.set_locale(ctx.guild, None)
            await ctx.send(
                embed=self.bot.build_embed(title, _("Default locale set."), "info"),
                hidden=True,
            )
            return
        try:
            locale = BabelLocale.parse(language_code, sep="-")
        except (ValueError, UnknownLocaleError):
            await ctx.send(
                embed=self.bot.build_embed(
                    title, _("Invalid language code. Use format: `en-US`"), "error"
                ),
                hidden=True,
            )
            return
        if locale.territory is None:
            await ctx.send(
                embed=self.bot.build_embed(
                    title, _("Invalid language code. Use format: `en-US`"), "error"
                ),
                hidden=True,
            )
            return
        standardized_locale_name = f"{locale.language}-{locale.territory}"
        i18n.set_contextual_locale(standardized_locale_name)
        await self.bot._i18n_cache.set_locale(ctx.guild, standardized_locale_name)
        await ctx.send(
            embed=self.bot.build_embed(
                title, _("Locale set to `{}`.").format(standardized_locale_name), "info"
            ),
            hidden=True,
        )

    @cog_ext.cog_slash(
        name="regionalformat",
        description="Changes bot's regional format in this server. This is used for formatting date, time and numbers.",
        options=[
            create_option(
                "language_code",
                "can be any language code with country code included, e.g. `en-US`, `de-DE`, `fr-FR`, `pl-PL`, etc.",
                3,
                True,
            )
        ],
    )
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def regionalformat(
        self, ctx: SlashContext, language_code: str = None
    ) -> None:
        """
        Changes bot's regional format in this server. This
        is used for formatting date, time and numbers.

        `<language_code>` can be any language code with country code included,
        e.g. `en-US`, `de-DE`, `fr-FR`, `pl-PL`, etc.

        Leave `<language_code>` empty to base regional formatting on
        bot's locale in this server.
        """
        title = _("Changing Regional Formant")
        if language_code is None:
            i18n.set_contextual_regional_format(None)
            await self.bot._i18n_cache.set_regional_format(ctx.guild, None)
            await ctx.send(
                embed=self.bot.build_embed(
                    title,
                    _(
                        "Regional formatting will now be based on bot's locale in this server."
                    ),
                    "info",
                ),
                hidden=True,
            )
            return
        try:
            locale = BabelLocale.parse(language_code, sep="-")
        except (ValueError, UnknownLocaleError):
            await ctx.send(
                embed=self.bot.build_embed(
                    title, _("Invalid language code. Use format: `en-US`"), "error"
                ),
                hidden=True,
            )
            return
        if locale.territory is None:
            await ctx.send(
                embed=self.bot.build_embed(
                    title, _("Invalid language code. Use format: `en-US`"), "error"
                ),
                hidden=True,
            )
        standardized_locale_name = f"{locale.language}-{locale.territory}"
        i18n.set_contextual_regional_format(standardized_locale_name)
        await self.bot._i18n_cache.set_regional_format(
            ctx.guild, standardized_locale_name
        )
        await ctx.send(
            embed=self.bot.build_embed(
                title,
                _("Regional formatting set to `{}`.").format(standardized_locale_name),
                "info",
            ),
            hidden=True,
        )

    @cog_ext.cog_subcommand(
        base="account",
        name="link",
        description="Link minecraft account from discord account.",
        options=[
            create_option(
                "username", "username to link your Discord account to.", 3, True
            )
        ],
    )
    async def account_link(self, ctx: SlashContext, username: str):
        profile_info = await self.bot.mojang_player(ctx.author, username)
        uuid: str = profile_info["uuid"]
        await self.bot._account_cache.set_account(ctx.author, uuid)
        await ctx.send(
            embed=self.bot.build_embed(
                _("Account linked"),
                _("Your account has been linked to {uuid}").format(uuid=uuid),
                "info",
            ),
            hidden=True,
        )

    @cog_ext.cog_subcommand(
        base="account",
        name="unlink",
        description="Unlink minecraft account from discord account.",
    )
    async def account_unlink(self, ctx: SlashContext) -> None:
        title = _("Account unlinked")
        if await self.bot._account_cache.get_account(ctx.author) is not None:
            await self.bot._account_cache.set_account(ctx.author, None)
            description = _(
                "Your account has been unlinked from any minecraft account."
            )
        else:
            description = _(
                "You don't have any account linked to your discord account."
            )
        await ctx.send(
            embed=self.bot.build_embed(title, description, "info"), hidden=True
        )

    @cog_ext.cog_subcommand(
        base="serverlink",
        name="link",
        description="Link minecraft server from discord server.",
        options=[
            create_option("server", "username to link your Discord server to.", 3, True)
        ],
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def serverlink_link(self, ctx: SlashContext, server: str) -> None:
        """Link Minecraft server to Discord guild."""
        await self.bot._guild_cache.set_server(ctx.guild, server)
        await ctx.send(
            embed=self.bot.build_embed(
                _("Server linked"),
                _("Your server has been linked to {server}").format(server=server),
                "info",
            ),
            hidden=True,
        )

    @cog_ext.cog_subcommand(
        base="serverlink",
        name="unlink",
        description="unlink minecraft server from discord server.",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def serverlink_unlink(self, ctx: SlashContext) -> None:
        """Unlink minecraft server from discord guild."""
        if await self.bot._guild_cache.get_server(ctx.guild) is not None:
            await self.bot._guild_cache.set_server(ctx.guild, None)
            description = _("Your server has been unlinked from any Minecraft server.")
        else:
            description = _("You don't have any server linked to your Discord guild.")
        await ctx.send(
            embed=self.bot.build_embed(_("Server unlinked"), description, "info"),
            hidden=True,
        )

    @cog_ext.cog_subcommand(
        base="autopost",
        name="setup",
        description="Setup Autopost.",
        options=[
            create_option(
                name="release",
                description="Channel to post Minecraft releases in.",
                option_type=7,
                required=False,
            ),
            create_option(
                name="snapshot",
                description="Channel to post Minecraft snapshots in.",
                option_type=7,
                required=False,
            ),
            create_option(
                name="article",
                description="Channel to post Minecraft articles in.",
                option_type=7,
                required=False,
            ),
            create_option(
                name="status",
                description="Channel to post Minecraft system statuses in.",
                option_type=7,
                required=False,
            ),
        ],
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def autopost_setup(
        self,
        ctx: SlashContext,
        release: Optional[discord.TextChannel] = None,
        snapshot: Optional[discord.TextChannel] = None,
        article: Optional[discord.TextChannel] = None,
        status: Optional[discord.TextChannel] = None,
    ) -> None:
        """Autopost Minecraft news and updates."""
        autopost_config: NewsType = {
            "release": release.id if release is not None else None,
            "snapshot": snapshot.id if snapshot is not None else None,
            "article": article.id if article is not None else None,
            "status": status.id if status is not None else None,
        }
        await self.bot._guild_cache.set_news(ctx.guild, autopost_config)
        embed = self.bot.build_embed(
            _("Autopost configuration updated"),
            _("Your server's autopost configuration has been updated."),
            "info",
        )
        if release is not None and type(release) is discord.TextChannel:
            embed.add_field(
                name=_("Release channel"),
                value=release.mention,
                inline=False,
            )
        if snapshot is not None and type(snapshot) is discord.TextChannel:
            embed.add_field(
                name=_("Snapshot channel"),
                value=snapshot.mention,
                inline=False,
            )
        if article is not None and type(article) is discord.TextChannel:
            embed.add_field(
                name=_("Article channel"),
                value=article.mention,
                inline=False,
            )
        if status is not None and type(status) is discord.TextChannel:
            embed.add_field(
                name=_("Status channel"),
                value=status.mention,
                inline=False,
            )
        await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_subcommand(
        base="autopost",
        name="view",
        description="View Autopost settings.",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def autopost_view(self, ctx: SlashContext) -> None:
        """View Autopost settings."""
        news = await self.bot._guild_cache.get_news(ctx.guild)
        if news is None:
            embed = self.bot.build_embed(
                _("Autopost configuration not set"),
                _("You don't have any Autopost configuration set."),
                "warning",
            )
            await ctx.send(embed=embed, hidden=True)
            return
        embed = self.bot.build_embed(
            _("Autopost configuration"),
            _("Your server's autopost configuration is as follows:"),
            "info",
        )
        if news["release"] is not None:
            embed.add_field(
                name=_("Release channel"),
                value=self.bot.get_channel(news["release"]).mention,
                inline=False,
            )
        if news["snapshot"] is not None:
            embed.add_field(
                name=_("Snapshot channel"),
                value=self.bot.get_channel(news["snapshot"]).mention,
                inline=False,
            )
        if news["article"] is not None:
            embed.add_field(
                name=_("Article channel"),
                value=self.bot.get_channel(news["article"]).mention,
                inline=False,
            )
        if news["status"] is not None:
            embed.add_field(
                name=_("Status channel"),
                value=self.bot.get_channel(news["status"]).mention,
                inline=False,
            )
        await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_subcommand(
        base="autopost",
        name="remove",
        description="Remove Autopost settings.",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def autopost_remove(self, ctx: SlashContext) -> None:
        """Remove Autopost settings."""
        await self.bot._guild_cache.set_news(ctx.guild, None)
        embed = self.bot.build_embed(
            _("Autopost configuration removed"),
            _("Your server's autopost configuration has been removed."),
            "info",
        )
        await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_subcommand(
        base="autopost",
        name="test",
        description="Test Autopost settings.",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def autopost_test(self, ctx: SlashContext) -> None:
        """View Autopost settings."""
        news = await self.bot._guild_cache.get_news(ctx.guild)
        if news is None:
            await ctx.send(
                embed=self.bot.build_embed(
                    _("Autopost configuration"),
                    _("Your server's autopost configuration is not set."),
                    "warning",
                ),
                hidden=True,
            )
            return
        if (
            news["release"] is not None
            and self.bot.get_channel(news["release"]) is not None
        ):
            release = self.bot.get_channel(news["release"])
            embed = self.bot.build_embed(
                _("Autopost Release Test"),
                _(
                    "Testing Autopost configuration for release channel {channel}..."
                ).format(
                    channel=release.mention,
                ),
                "info",
            )
            await release.send(embed=embed)
        if (
            news["snapshot"] is not None
            and self.bot.get_channel(news["snapshot"]) is not None
        ):
            snapshot = self.bot.get_channel(news["snapshot"])
            embed = self.bot.build_embed(
                _("Autopost Snapshot Test"),
                _(
                    "Testing Autopost configuration for snapshot channel {channel}..."
                ).format(
                    channel=snapshot.mention,
                ),
                "info",
            )
            await snapshot.send(embed=embed)
        if (
            news["article"] is not None
            and self.bot.get_channel(news["article"]) is not None
        ):
            article = self.bot.get_channel(news["article"])
            embed = self.bot.build_embed(
                _("Autopost Article Test"),
                _(
                    "Testing Autopost configuration for article channel {channel}..."
                ).format(
                    channel=article.mention,
                ),
                "info",
            )
            await article.send(embed=embed)
        if (
            news["status"] is not None
            and self.bot.get_channel(news["status"]) is not None
        ):
            status = self.bot.get_channel(news["status"])
            embed = self.bot.build_embed(
                _("Autopost Status Test"),
                _(
                    "Testing Autopost configuration for status channel {channel}..."
                ).format(
                    channel=status.mention,
                ),
                "info",
            )
            await status.send(embed=embed)
        embed = self.bot.build_embed(
            _("Autopost Test Results"),
            _("Test messages have been sent to each channel"),
            "info",
        )
        await ctx.send(embed=embed, hidden=True)
