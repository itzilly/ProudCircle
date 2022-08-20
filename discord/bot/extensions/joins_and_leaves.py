import pytz
import discord
import logging

from util import randoms
from datetime import datetime
from discord.ext import commands
from util.config_handler import Settings


class DiscordListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.debug(f"| MEMBER JOIN EVENT | {member.name}#{member.discriminator} joined (id: {member.id})")
        welcome_channel = self.bot.get_channel(Settings.config['discord']['channel_ids']['welcome'])
        rules_channel = self.bot.get_channel(Settings.config['discord']['channel_ids']['rules'])
        verification_channel = self.bot.get_channel(Settings.config['discord']['channel_ids']['verification'])
        join_embed_files = []
        join_embed = discord.Embed(title="Welcome to the Proud Circle Community Discord!", colour=randoms.embed_color())
        join_embed_files.append(discord.File("./data/images/icon.png", filename="icon.png"))
        join_embed.set_thumbnail(url="attachment://icon.png")
        join_embed.timestamp = datetime.now(tz=pytz.timezone('EST'))
        join_embed.add_field(name=randoms.join_message(),
                             value=f"\nWelcome {member.mention}!\n"
                             f"Please be sure to:\n1    verify your account in {verification_channel.mention}"
                             f"\n2    read {rules_channel.mention}\nbefore continuing!\nWe hope you enjoy your stay!\n")
        await welcome_channel.send(files=join_embed_files, embed=join_embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logging.debug(f"| MEMBER LEAVE EVENT | {member.name}#{member.discriminator} joined (id: {member.id})")
        channel = self.bot.get_channel(Settings.config['discord']['channel_ids']['leave'])
        leave_embed = discord.Embed(
            description=f"Sorry to see you go {member.mention} :wave:",
            colour=randoms.embed_color()
        )
        await channel.send(embed=leave_embed)


async def setup(bot: commands.Bot):
    logging.debug("Adding Cog: DiscordListener")
    await bot.add_cog(DiscordListener(bot))
