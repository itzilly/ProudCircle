import asyncio
import discord
import logging
from discord import Activity
from discord.ext import tasks, commands
from discord.enums import ActivityType
from datetime import datetime, timedelta


class PresenceSwitcher(commands.Cog):
    def __init__(self, bot: commands.Bot, *args, **kwargs):
        self.bot = bot
        self.show_discord_members = True
        super().__init__(*args, **kwargs)

    @tasks.loop(seconds=10)
    async def presence_switcher(self):
        online_discord_members = 0
        total_discord_members = 0
        if self.show_discord_members:
            presence = Activity(name=f"{total_discord_members} total discord members", type=ActivityType.playing)
        else:
            presence = Activity(name=f"{online_discord_members} online discord members", type=ActivityType.watching)

        await self.bot.change_presence(activity=presence)

    @presence_switcher.before_loop
    async def before_switching_presence(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    logging.debug("Adding cog: SetupCommands")
    await bot.add_cog(PresenceSwitcher(bot))
