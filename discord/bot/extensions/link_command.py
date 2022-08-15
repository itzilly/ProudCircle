import time
import discord
import logging
import requests
import datetime

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

        commands_channel = interaction.guild.get_channel(Settings.config['discord']['channel_ids']['bot_commands'])
        linking_tutorial_embed = discord.Embed()
        linking_tutorial_embed.colour = discord.Colour(0xfa1195)
        linking_tutorial_embed.add_field(
            name="How to link your account:",
            value="`#1` Log onto hypixel.net\n"
                  "`#2` Right click on your head (hotbar)\n"
                  "`#3` Select 'Social Media' in the GUI\n"
                  "`#4` Select 'Discord' and paste your discord (eg: illyum#4466) in chat\n"
                  "`#5` Use /link in {}".format(commands_channel.mention))

        if discord_id is None:
            await interaction.response.send_message(embed=linking_tutorial_embed)
            return False

        if discord_id == f"{interaction.user.name}#{interaction.user.discriminator}":
            database_entry = {
                'uuid': player.uuid,
                'discord_id': interaction.user.id,
                'discord_name': interaction.user.name,
                'discord_discriminator': interaction.user.discriminator,
                'discord_display_name': interaction.user.display_name,
                'time_linked': f"{time.time()}",
                'datetime_linked': f"{datetime.now()}",
                'force_linked': False,
                'force_linked_by': None
            }
            LinkedDatabase.add_entry(database_entry)
            await interaction.response.send_message(f"Linked {player.name} with {discord_id}")
        else:
            await interaction.response.send_message(embed=linking_tutorial_embed)


async def setup(bot):
    logging.debug("Adding cog: LinkCommand")
    await bot.add_cog(LinkCommand(bot))
