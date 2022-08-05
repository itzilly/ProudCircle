import logging

from discord import Activity
from discord.enums import ActivityType
from discord.ext import tasks, commands
from util.config_handler import Settings


class PresenceSwitcher(commands.Cog):
    def __init__(self, bot: commands.Bot, *args, **kwargs):
        self.bot = bot
        self.show_discord_members = True
        if Settings.config['discord']['roles_have_been_created']:
            self.presence_switcher.start()
        super().__init__(*args, **kwargs)

    @tasks.loop(seconds=10)
    async def presence_switcher(self):
        guild = self.bot.get_guild(Settings.config['discord']['server_id'])
        total_members = len(guild.members)

        if self.show_discord_members:
            presence = Activity(name=f"{total_members} total discord members", type=ActivityType.playing)
            self.show_discord_members = False
        else:
            online = 0
            for member in guild.members:
                if member.is_on_mobile() or member.status.online or member.status.idle or member.status.do_not_disturb:
                    online += 1

            presence = Activity(name=f"{online} online discord members", type=ActivityType.watching)
            self.show_discord_members = True

        await self.bot.change_presence(activity=presence)

    @presence_switcher.before_loop
    async def before_switching_presence(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    logging.debug("Adding cog: PresenceSwitcher")
    await bot.add_cog(PresenceSwitcher(bot))
