import logging

import discord

from discord.ext import commands
from util.config_handler import Settings


class VerificationListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_id = Settings.config['discord']['message_ids']['verification_id']
        self.emoji_to_role = {
            discord.PartialEmoji(name='☑️'): Settings.config['discord']['role_ids']['verified'],
            discord.PartialEmoji(name='☑'): Settings.config['discord']['role_ids']['guild_member'],
        }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.message_id:
            return

        try:
            verified_role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return

        verified_role = self.bot.get_guild(payload.guild_id).get_role(verified_role_id)
        await payload.member.add_roles(verified_role)


async def setup(bot):
    logging.debug("Setting up VerificationListener")
    await bot.add_cog(VerificationListener(bot))
