import pytz
import time
import sqlite3
import discord
import logging
import requests

from util import fs
from util.mcign import MCIGN
from discord import app_commands
from discord.ext import commands
from util.config_handler import Settings


how_to_link = discord.Embed(colour=discord.Colour(0xfa1195))
how_to_link.add_field(
    name="How to link your discord account on hypixel:",
    value="`#1` Go to any game lobby and right click on your head in your hotbar.\n"
          "`#2` In the GUI, select 'Social Media'. It looks like a twitter head.\n"
          "`#3` Left click the discord head in the new popup.\n"
          "`#4` Copy your discord username#number and paste in game chat!")


class LinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
            await interaction.response.send_message(embed=how_to_link)
            return False

        # Discord id matches command sender
        if discord_id == f"{interaction.user.name}#{interaction.user.discriminator}":
            # Check if account has already been linked with that username/discord handle
            command = f"SELECT discord_id, player_uuid FROM discord_link WHERE discord_id is {interaction.user.id}"
            execute = fs.con.execute(command)
            response = execute.fetchall()
            if len(response) == 0:  # Not linked
                # Logic to link account (save to database)
                command = f"INSERT INTO discord_link VALUES ({interaction.user.id}, '{player_name}', '{player_uuid}')"
                execute = fs.con.cursor().execute(command)
                fs.con.commit()
                embed = discord.Embed(
                    colour=discord.Colour(0xf00c27),
                    description=f"Linked {interaction.user.mention} with {player_name}!"
                )
                await interaction.response.send_message(embed=embed)
            else:  # Account has already been linked
                embed = discord.Embed(
                    colour=discord.Colour(0xf00c27),
                    description="Your account is already linked! If you would like to unlink your account, use /unlink"
                )
                await interaction.response.send_message(embed=embed)
        # Discord id is present but does not match command sender
        else:
            linking = how_to_link
            linking.title = "Please make sure you've typed the right discord account on your hypixel profile!"
            await interaction.response.send_message(embed=linking)


class UnlinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unlink", description="Unlink your account from this discord server")
    async def unlink(self, interaction: discord.Interaction):
        """Unlink discord account with minecraft account"""
        # Check if account is linked or not
        command = f"SELECT * FROM discord_link WHERE discord_id IS {interaction.user.id}"
        execute = fs.con.execute(command)
        response = execute.fetchall()
        # Command sender account is not linked
        if len(response) == 0:
            embed = discord.Embed(
                colour=discord.Colour(0xf00c27),
                description="Your account is not linked, therefore you can't use this command!"
            )
            await interaction.response.send_message(embed=embed)
            return False
        else:
            command = f"DELETE FROM discord_link WHERE discord_id IS {interaction.user.id}"
            execute = fs.con.execute(command)
            fs.con.commit()
            embed = discord.Embed(
                colour=discord.Colour(0x1bb510),
                description=":white_check_mark: Your account was successfully unlinked!"
            )
            await interaction.response.send_message(embed=embed)
            return True


# Add link and unlink commands to bot
async def setup(bot: commands.Bot):
    logging.debug("Adding cog: LinkCommand")
    await bot.add_cog(LinkCommand(bot))
    logging.debug("Adding Cog: UnlinkCommand")
    await bot.add_cog(UnlinkCommand(bot))
