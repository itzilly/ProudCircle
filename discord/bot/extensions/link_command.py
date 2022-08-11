import datetime
import time
import logging
import discord
import requests

from datetime import datetime
from util.mcign import MCIGN
from util.config_handler import Settings
from util.linked_database import LinkedDatabase
from discord import app_commands
from discord.ext import commands


class LinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="link")
    async def link(self, interaction: discord.Interaction, username: str):
        """Links discord and hypixel minecraft account"""
        key = Settings.config['hypixel']['api_key']
        player = MCIGN(id=username)
        uri = "https://api.hypixel.net/player?key={}&uuid={}".format(key, player.uuid)
        data = requests.get(uri).json()
        player_data = data.get("player", {})
        social_media = player_data.get("socialMedia", {})
        media_links = social_media.get("links", {})
        discord_id = media_links.get("DISCORD", None)
        if discord_id is None:
            await interaction.response.send_message("Please link your discord account on hypixel")
            return False

        if discord_id == f"{interaction.user.name}#{interaction.user.discriminator}":
            database_entry = {
                'uuid': player.uuid,
                'discord_id': interaction.user.id,
                'discord_name': interaction.user.name,
                'discord_discriminator': interaction.user.discriminator,
                'discord_display_name': interaction.user.display_name,
                'time_linked': f"{time.time()}",
                'datetime_linked': f"{datetime.now()}"
            }
            LinkedDatabase.add_entry(database_entry)
            await interaction.response.send_message(f"Linked {player.name} with {discord_id}")
        else:
            await interaction.response.send_message(f"Please link your discord account on hypixel!")


async def setup(bot):
    logging.debug("Adding cog: LinkCommand")
    await bot.add_cog(LinkCommand(bot))
