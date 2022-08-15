import discord
import logging
import requests
import util.config_handler

from util.mcign import MCIGN
from discord import app_commands
from discord.ext import commands


class CoinsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="coins")
    async def coinsCommand(self, interaction: discord.Interaction, username: str):
        player = MCIGN(id=username)
        uuid = player.uuid
        name = player.name
        api_key = util.config_handler.Settings.config['hypixel']['api_key']
        uri = "https://api.hypixel.net/player?key={}&uuid={}".format(api_key, uuid)
        coins = requests.get(uri).json()['player']['stats']['Bedwars']['coins']
        await interaction.response.send_message(f"{name} has {coins} coins!")


async def setup(bot: commands.Bot) -> None:
    logging.debug("Adding cog: CoinsCommand")
    await bot.add_cog(CoinsCommand(bot))
