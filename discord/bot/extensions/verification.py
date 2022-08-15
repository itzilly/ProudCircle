import discord
import logging

from discord.ext import commands
from util.config_handler import Settings


class VerificationListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_id = Settings.config['discord']['message_ids']['verification_id']

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.message_id:
            return
        if payload.emoji.name == "☑️":
            verified_role_id = Settings.config['discord']['role_ids']['verified']
            verified_role = self.bot.get_guild(payload.guild_id).get_role(verified_role_id)
            try:
                await payload.member.add_roles(verified_role)
                logging.info(f"User {payload.member.id} ({payload.member.name}#{payload.member.discriminator}) has just been verified!")
            except Exception as e:
                logging.critical(e)


async def setup(bot):
    logging.debug("Setting up VerificationListener")
    await bot.add_cog(VerificationListener(bot))
