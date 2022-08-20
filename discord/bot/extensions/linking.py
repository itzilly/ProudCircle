import pytz
import time
import sqlite3
import discord
import logging
import requests

from util.mcign import MCIGN
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from util.config_handler import Settings


class LinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.con = sqlite3.connect('./data/discord.db')

    @app_commands.command(name="link", description="Link your account to this discord server")
    async def link(self, interaction: discord.Interaction, username: str):
        """Links discord account with minecraft account"""
        key = Settings.config['hypixel']['api_key']
        player = MCIGN(id=username)
        player_uuid = player.uuid
        player_name = player.name
        uri = "https://api.hypixel.net/player?key={}&uuid={}".format(key, player.uuid)
        data = requests.get(uri).json()
        discord_id = data.get('player', {}).get("socialMedia", {}).get("links").get("DISCORD", None)

        # No discord handle has been set by player 'username'
        if discord_id is None:
            await interaction.response.send_message("Please link your discord account on hypixel!")
            return False

        # Discord id matches command sender
        if discord_id == f"{interaction.user.name}#{interaction.user.discriminator}":
            # Check if account has already been linked with that username/discord handle
            command = f"SELECT discord_id, player_uuid FROM discord_link WHERE discord_id is {interaction.user.id}"
            execute = self.con.cursor().execute(command)
            response = execute.fetchall()
            if len(response) == 0:  # Not linked
                # Logic to link account (save to database)
                command = f"INSERT INTO discord_link VALUES ({interaction.user.id}, '{player_name}', '{player_uuid}')"
                execute = self.con.cursor().execute(command)
                await interaction.response.send_message(f"Linked {interaction.user.mention} with {player_name}!")
            else:  # Account has already been linked
                await interaction.response.send_message("Your account is already linked! If you would like to unlink "
                                                        "your account, use /unlink")
        # Discord id is present but does not match command sender
        else:
            await interaction.response.send_message("Please make sure you've typed the right discord account on your "
                                                    "hypixel profile!")


class UnlinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.con = sqlite3.connect('./data/discord.db')

    @app_commands.command(name="unlink", description="Unlink your account from this discord server")
    async def unlink(self, interaction: discord.Interaction):
        """Unlink discord account with minecraft account"""
        # Check if account is linked or not
        command = f"SELECT * FROM discord_link WHERE discord_id IS {interaction.user.id}"
        execute = self.con.execute(command)
        response = execute.fetchall()
        # Command sender account is not linked
        if len(response) == 0:
            await interaction.response.send_message("Your account is not linked, therefore you can't use this command!")
            return False
        else:
            command = f"DELETE FROM discord_link WHERE discord_id IS {interaction.user.id}"
            execute = self.con.execute(command)
            await interaction.response.send_message("Your account was successfully unlinked!")
            return True


# Add link and unlink commands to bot
async def setup(bot: commands.Bot):
    logging.debug("Adding cog: LinkCommand")
    await bot.add_cog(LinkCommand(bot))
    logging.debug("Adding Cog: UnlinkCommand")
    await bot.add_cog(UnlinkCommand(bot))
