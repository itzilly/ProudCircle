import discord
import logging

from util import local
from discord import app_commands
from discord.ext import commands
from util.command_helper import ensure_bot_permissions


class ClearCacheCommand(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.local_data = local.LOCAL_DATA

	@app_commands.command(name="clearcache", description="Remove a cache (Admins Only)")
	async def ping(self, interaction: discord.Interaction, cache_name: str):
		has_permissions = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permissions:
			return

		if cache_name.lower() == "uuidcache":
			self.local_data.uuid_cache.clear_cache(confirm=True)
		completed_embed = discord.Embed(
			colour=discord.Colour(0xd69f06),
			title="Cache Handler",
			description="Cleared uuidCache"
		)
		await interaction.response.send_message(embed=completed_embed)


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: ClearCacheCommand")
	await bot.add_cog(ClearCacheCommand(bot))
