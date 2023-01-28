import logging

import discord
from discord import app_commands
from discord.ext import tasks, commands

from util import local, embed_lib
from util.command_helper import ensure_bot_permissions


class LeaderboardUpdater(commands.Cog):
	def __init__(self, bot: commands.Bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot
		# self.my_task.start()
		self.message = None
		self.config: local.ConfigHandler = local.LOCAL_DATA.config
		self.server_id = int(self.config.get_setting("server_id"))

		self.lb_division_message = self.config.get_setting("lb_division_id")
		self.lb_lifetime_message = self.config.get_setting("lb_lifetime_gexp_id")
		self.lb_yearly_message = self.config.get_setting("lb_yearly_gexp_id")
		self.lb_monthly_message = self.config.get_setting("lb_monthly_gexp_id")
		self.lb_weekly_message = self.config.get_setting("lb_weekly_gexp_id")
		self.lb_daily_message = self.config.get_setting("lb_daily_gexp_id")

		self.lb_channel = None

		self.setup_channel_task.start()

	@tasks.loop(hours=1)
	async def setup_channel_task(self):
		lb_channel_id = self.config.get_setting("leaderboard_channel")
		if lb_channel_id is not None:
			self.lb_channel = self.bot.get_guild(self.server_id).get_channel(int(lb_channel_id))
		self.setup_channel_task.stop()

	@setup_channel_task.before_loop
	async def before_setup_channel_task(self):
		await self.bot.wait_until_ready()

	@tasks.loop(minutes=30)
	async def my_task(self):
		logging.debug("Running LeaderboardUpdater Task")
		await self.message.edit(embed=discord.Embed(description="This is a test!"))

	@my_task.before_loop
	async def before_exp_logger_init(self):
		await self.bot.wait_until_ready()

	@app_commands.command(name="create-leaderboards", description="Initiate leaderboard setup (Admins Only)")
	async def create_leaderboards_command(self, interaction: discord.Interaction, leaderboards_channel: str = None):
		has_permissions = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permissions:
			return

		if leaderboards_channel is not None:
			self.lb_channel = self.bot.get_guild(self.server_id).get_channel(int(leaderboards_channel))
			self.config.set_setting("leaderboard_channel", leaderboards_channel)

		if self.lb_channel is None:
			await interaction.response.send_message(embed=embed_lib.UnknownErrorEmbed())
			return

		await self.lb_channel.send("Re-Generating the leaderboard messages")

		division_lb_message = await self.lb_channel.send(embed=discord.Embed(title="This is the division leaderboard"))
		self.config.set_setting("lb_division_id", f"{division_lb_message.id}")

		lifetime_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the lifetime gexp leaderboard"))
		self.config.set_setting("lb_lifetime_gexp_id", f"{lifetime_lb_message.id}")

		yearly_lb_message = await self.lb_channel.send(embed=discord.Embed(title="This is the yearly gexp leaderboard"))
		self.config.set_setting("lb_yearly_gexp_id", f"{yearly_lb_message.id}")

		monthly_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the monthly gexp leaderboard"))
		self.config.set_setting("lb_monthly_gexp_id", f"{monthly_lb_message.id}")

		weekly_lb_message = await self.lb_channel.send(embed=discord.Embed(title="This is the weekly gexp leaderboard"))
		self.config.set_setting("lb_weekly_gexp_id", f"{weekly_lb_message.id}")

		daily_lb_message = await self.lb_channel.send(embed=discord.Embed(title="This is the daily gexp leaderboard"))
		self.config.set_setting("lb_daily_gexp_id", f"{daily_lb_message.id}")

		finished_embed = discord.Embed()
		finished_embed.description = "Created leaderboards!"
		await interaction.response.send_message(embed=finished_embed)


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: LeaderboardUpdater")
	await bot.add_cog(LeaderboardUpdater(bot))
