import time
import discord
import logging
import requests
import datetime
import util.command_helper

from util.mcign import MCIGN
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from util.config_handler import Settings
from util.linked_database import LinkedDatabase


class ForceLinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="forcelink")
    async def force_link(self, interaction: discord.Interaction, playername: str, user_id: str):
        """Force link (aka run command for someone else)"""
        if not util.command_helper.check_permission(interaction.user, level=""):
            embed = discord.Embed(
                description=":x:  You do not have permission to use this command!  :x:",
                colour=discord.Colour(0xfa1195)
            )
            return await interaction.response.send_message(embed=embed)

        key = Settings.config['hypixel']['api_key']
        player = MCIGN(id=playername)
        uri = "https://api.hypixel.net/player?key={}&uuid={}".format(key, player.uuid)
        data = requests.get(uri).json()
        player_data = data.get("player", {})
        social_media = player_data.get("socialMedia", {})
        media_links = social_media.get("links", {})
        discord_id = media_links.get("DISCORD", None)
        if discord_id is None:
            await interaction.response.send_message("Error linking {}".format(playername))

        _user = self.bot.get_user(int(user_id))
        if discord_id == f"{_user.name}#{_user.discriminator}":
            database_entry = {
                'uuid': player.uuid,
                'discord_id': user_id,
                'discord_name': _user.name,
                'discord_discriminator': _user.discriminator,
                'discord_display_name': _user.display_name,
                'time_linked': f"{time.time()}",
                'datetime_linked': f"{datetime.now()}",
                'force_linked': True,
                'force_linked_by': interaction.user.id
            }
            LinkedDatabase.add_entry(database_entry)
            await interaction.response.send_message(f"Force linked {player.name} with {_user.mention}")
        else:
            await interaction.response.send_messate("Force link failed!")


async def setup(bot):
    logging.debug("Adding cog: ForceLinkCommand")
    await bot.add_cog(ForceLinkCommand(bot))