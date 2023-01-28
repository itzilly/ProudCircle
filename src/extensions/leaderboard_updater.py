import datetime
import json
import logging
import time

import discord
from discord import app_commands
from discord.ext import tasks, commands

from util import local, embed_lib
from util.command_helper import ensure_bot_permissions

from util.local import XP_DIVISION_DATA_PATH


class LeaderboardUpdater(commands.Cog):
	def __init__(self, bot: commands.Bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot
		self.local: local.LocalData = local.LOCAL_DATA
		self.config: local.ConfigHandler = self.local.config
		self.server_id = int(self.config.get_setting("server_id"))

		with open(XP_DIVISION_DATA_PATH, encoding='utf-8') as json_file:
			self.roles_data = json.load(json_file)

		self.lb_division_message_id = self.config.get_setting("lb_division_id")
		self.lb_lifetime_message_id = self.config.get_setting("lb_lifetime_gexp_id")
		self.lb_yearly_message_id = self.config.get_setting("lb_yearly_gexp_id")
		self.lb_monthly_message_id = self.config.get_setting("lb_monthly_gexp_id")
		self.lb_weekly_message_id = self.config.get_setting("lb_weekly_gexp_id")
		self.lb_daily_message_id = self.config.get_setting("lb_daily_gexp_id")

		self.lb_division_message = None
		self.lb_lifetime_message = None
		self.lb_yearly_message = None
		self.lb_monthly_message = None
		self.lb_weekly_message = None
		self.lb_daily_message = None

		self.lb_channel = None

		self.setup_channel_task.start()

		self.has_run_divisions = False
		self.has_run_lifetime = False
		self.has_run_yearly = False
		self.has_run_monthly = False
		self.has_run_weekly = False
		self.has_run_daily = False

	@tasks.loop(hours=1)
	async def setup_channel_task(self):
		lb_channel_id = self.config.get_setting("leaderboard_channel")
		if lb_channel_id is not None:
			self.lb_channel = self.bot.get_guild(self.server_id).get_channel(int(lb_channel_id))
		self.setup_channel_task.stop()

		self.lb_division_message = self.lb_channel.guild.fetch_channel(int(self.lb_division_message_id))
		if self.lb_division_message is not None:
			self.division_leaderboard_task.start()

	@setup_channel_task.before_loop
	async def before_setup_channel_task(self):
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

		await interaction.response.defer()

		async for chat in self.lb_channel.history(
				limit=21):  # Each lb is 7 messages, so delete up to last 3 leaderboards
			if chat.author.id == self.bot.user.id:
				await chat.delete()

		await self.lb_channel.send("Re-Generating the leaderboard messages...")

		division_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the division leaderboard"))
		self.config.set_setting("lb_division_id", f"{division_lb_message.id}")
		finished_division_leaderboard = await self.update_division_leaderboard()

		lifetime_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the lifetime gexp leaderboard"))
		self.config.set_setting("lb_lifetime_gexp_id", f"{lifetime_lb_message.id}")

		yearly_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the yearly gexp leaderboard"))
		self.config.set_setting("lb_yearly_gexp_id", f"{yearly_lb_message.id}")

		monthly_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the monthly gexp leaderboard"))
		self.config.set_setting("lb_monthly_gexp_id", f"{monthly_lb_message.id}")

		weekly_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the weekly gexp leaderboard"))
		self.config.set_setting("lb_weekly_gexp_id", f"{weekly_lb_message.id}")

		daily_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the daily gexp leaderboard"))
		self.config.set_setting("lb_daily_gexp_id", f"{daily_lb_message.id}")

		finished_embed = discord.Embed()
		finished_embed.description = "Created leaderboards!"
		await interaction.followup.send(embed=finished_embed)

	@tasks.loop(hours=2)
	async def division_leaderboard_task(self) -> None:
		if not self.has_run_divisions:
			self.has_run_divisions = True
			logging.debug("LeaderboardUpdater: Skipping first run (divisions)")
			return
		await self.update_division_leaderboard()

	@division_leaderboard_task.before_loop
	async def before_division_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_division_leaderboard(self) -> bool:
		# TODO: Only add players if they are currently in the guild
		try:
			division_data = await self.order_members_by_highest_role()
			embed_description_as_list = []
			position = 1
			for player in division_data:
				discord_member: discord.Member = player["member"]
				member = discord_member.mention
				highest_role_mention = self.lb_channel.guild.get_role(player["highest_division"]["role_id"]).mention
				highest_role = player["highest_division"]["discord_name"]
				if position == 1:
					embed_description_as_list.append(f":first_place:  {member}  -  {highest_role}")
				elif position == 2:
					embed_description_as_list.append(f":second_place:  {member}  -  {highest_role}")
				elif position == 3:
					embed_description_as_list.append(f":third_place:  {member}  -  {highest_role}")
					embed_description_as_list.append(" ========== ")
				else:
					embed_description_as_list.append(f"#{position}  {member}")
				position = position + 1

			division_lb = discord.Embed(timestamp=datetime.datetime.now())
			division_lb.title = "Division Leaderboards:"
			division_lb.colour = discord.Colour(0xffdf00)
			division_lb.description = '\n'.join(embed_description_as_list)
			await self.lb_division_message.edit(embed=division_lb)
			return True
		except Exception as e:
			logging.error(e)
			return False

	@app_commands.command(name="update-divisions-leaderboard", description="Force-update the divisions leaderboard (Admins Only)")
	async def update_divisions_leaderboard_command(self, interaction: discord.Interaction) -> None:
		has_permissions = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permissions:
			return

		logging.debug("Force-updating divisions leaderboard...")
		await interaction.response.defer()
		start_time = time.perf_counter()
		await self.update_division_leaderboard()
		end_time = time.perf_counter()
		response_embed = discord.Embed()
		response_embed.colour = discord.Colour(0x08a169)
		response_embed.description = f"Finished in f{end_time - start_time} seconds"
		await interaction.response.send_message(embed=response_embed)

	async def order_members_by_highest_role(self) -> list:
		data = []
		discord_members = self.bot.get_guild(self.server_id).members

		for member in discord_members:
			division_roles = []
			roles_ids = [r.id for r in member.roles]
			for json_role in self.roles_data["roles"]:
				if json_role["role_id"] in roles_ids:
					division_roles.append(json_role)
			division_roles = sorted(division_roles, key=lambda role: role["required_amount"], reverse=True)
			if len(division_roles) != 0:
				highest_role = division_roles[0]
				data.append({"member": member, "highest_division": highest_role})

		data = sorted(data, key=lambda x: x["highest_division"]["required_amount"], reverse=True)

		return data


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: LeaderboardUpdater")
	await bot.add_cog(LeaderboardUpdater(bot))
