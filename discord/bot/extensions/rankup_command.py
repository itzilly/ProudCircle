import logging
import discord
import requests

import util.config_handler
from util.mcign import MCIGN
from discord import app_commands
from discord.ext import commands


class RankupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="rankup")
    async def rankupCommand(self, interaction: discord.Interaction):
        config = util.config_handler.Settings.config
        api_key = config['hypixel']['api_key']
        guild_id = config['hypixel']['guid_id']
        uri = "https://api.hypixel.net/guild?key={}&id={}".format(api_key, guild_id)
        guild_members = requests.get(uri).json()['guild']['members']
        lb = []
        for member in guild_members:
            lb_entry = {}
            uuid = member['uuid']
            weekly_gexp = 0
            for key, value in member['expHistory'].items():
                weekly_gexp += value
            lb_entry['uuid'] = uuid
            lb_entry['weekly_gexp'] = weekly_gexp
            if weekly_gexp != 0:
                lb.append(lb_entry)

        leaderboard = sorted(lb, key=lambda d: d['weekly_gexp'], reverse=True)
        leaderboard = leaderboard[:10]

        message = "```\n"
        position = 1
        for line in leaderboard:
            if position == 1:
                role = "Champion"
            elif position == 2 or position == 3:
                role = "Celestial"
            else:
                role = "Legend"

            player = MCIGN(id=line['uuid'])
            _message = "#{} {} -> {} with {} gexp".format(
                position,
                player.name.replace('_', '\\_'),
                role,
                "{:,}".format(line['weekly_gexp'])
            )
            message = message + _message + '\n'
            position += 1
        message = message + "```"
        await interaction.response.send_message(message)


async def setup(bot: commands.Bot) -> None:
    logging.debug("Adding cog: RankupCommand")
    await bot.add_cog(RankupCommand(bot))
