import logging
import discord

from discord.ext import commands

from util.config_handler import Settings
from util.embed_builder import EmbedBuilder


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
        join_embed = EmbedBuilder()
        join_embed.set_title("A Wild Member has joined!")
        join_embed.use_default_thumbnail()
        join_embed.add_field("Hey There New Member!",
                             f"\nWelcome {member.mention} to the Proud Circle Discord Community!\n"
                             f"Please be sure verify your account in {verification_channel.mention} and "
                             f"read {rules_channel.mention} before continuing.\n\n")
        join_embed.use_default_footer = True
        await welcome_channel.send(files=join_embed.get_files(), embed=join_embed.build())

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logging.debug(f"| MEMBER LEAVE EVENT | {member.name}#{member.discriminator} joined (id: {member.id})")
        channel = self.bot.get_channel(Settings.config['discord']['channel_ids']['rules'])
        leave_embed = discord.Embed(
            description=f"Sorry to see you go {member.mention} :wave:",
            colour=discord.Colour(0xfa1195)
        )
        await channel.send(embed=leave_embed)


async def setup(bot: commands.Bot):
    logging.debug("Setup 'DiscordListener(commands.Cog)'")
    await bot.add_cog(DiscordListener(bot))
