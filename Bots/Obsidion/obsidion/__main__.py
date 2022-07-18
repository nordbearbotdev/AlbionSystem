"""Initialise and run the bot."""
import logging

from discord import Activity
from discord import ActivityType
from discord import AllowedMentions
from discord import Intents
from discord_slash import SlashCommand
from obsidion import _update_event_loop_policy
from obsidion.core import get_settings
from obsidion.core.bot import Obsidion

_update_event_loop_policy()

log = logging.getLogger("obsidion")


def main() -> None:
    """Main initialisation script."""
    # So no one can abuse the bot to mass mention
    allowed_mentions = AllowedMentions(everyone=False, roles=False, users=True)

    # As the bot functions off just slash commands
    # it only needs guild info to do some channel updating
    intents = Intents.none()
    intents.guilds = True

    # Allow messages for testing bot
    if get_settings().DEV:
        intents.messages = True
        intents.reactions = True

    activity = Activity(
        name=get_settings().ACTIVITY,
        type=ActivityType.watching,
    )

    args = {
        "description": "",
        "self_bot": False,
        "owner_ids": [],
        "activity": activity,
        "intents": intents,
        "allowed_mentions": allowed_mentions,
        "command_prefix": "$",
    }

    obsidion = Obsidion(**args)

    log.info("Ready to go, building everything")
    SlashCommand(obsidion, sync_commands=True, sync_on_cog_reload=True)
    log.info("Initialised slash commands")
    obsidion.run(get_settings().DISCORD_TOKEN)
    log.info("Obsidion shutting down")


if __name__ == "__main__":
    """Run the bot."""
    main()
