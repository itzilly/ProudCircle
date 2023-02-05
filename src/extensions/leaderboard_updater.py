import json
import time
import asyncio
import logging
import discord
import datetime

from discord import app_commands
from discord.ext import tasks, commands

import util.mcign
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

		self.has_run_divisions = False
		self.has_run_lifetime = False
		self.has_run_yearly = False
		self.has_run_monthly = False
		self.has_run_weekly = False
		self.has_run_daily = False

		asyncio.ensure_future(self.setup())

	async def setup(self) -> None:
		await self.bot.wait_until_ready()
		lb_channel_id = self.config.get_setting("leaderboard_channel")
		if lb_channel_id is not None:
			self.lb_channel = self.bot.get_guild(self.server_id).get_channel(int(lb_channel_id))

		self.lb_division_message = await self.lb_channel.fetch_message(int(self.lb_division_message_id))
		if self.lb_division_message is not None:
			logging.debug("Activating Division Leaderboard Task")
			self.division_leaderboard_task.start()

		self.lb_lifetime_message = await self.lb_channel.fetch_message(int(self.lb_lifetime_message_id))
		if self.lb_lifetime_message is not None:
			logging.debug("Activating Lifetime Gexp Leaderboard Task")
			self.lifetime_gexp_leaderboard_task.start()

		self.lb_yearly_message = await self.lb_channel.fetch_message(int(self.lb_yearly_message_id))
		if self.lb_yearly_message is not None:
			logging.debug("Activating Yearly Gexp Leaderboard Task")
			self.yearly_gexp_leaderboard_task.start()

	@tasks.loop(hours=2)
	async def division_leaderboard_task(self) -> None:
		if not self.has_run_divisions:
			self.has_run_divisions = True
			logging.info("LeaderboardUpdater: Skipping first run (divisions)")
			return
		logging.info("LeaderboardUpdater: Running Divisions Task")
		await self.update_division_leaderboard()

	@division_leaderboard_task.before_loop
	async def before_division_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_division_leaderboard(self) -> bool:
		logging.info("Updating Division Leaderboard")
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
		await interaction.edit_original_response(embed=response_embed)

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

	@tasks.loop(hours=2)
	async def lifetime_gexp_leaderboard_task(self) -> None:
		if not self.has_run_lifetime:
			self.has_run_lifetime = True
			logging.info("LeaderboardUpdater: Skipping first run (lifetime)")
			return
		logging.info("LeaderboardUpdater: Running Lifetime GEXP Task")
		await self.update_lifetime_gexp_leaderboard()

	@lifetime_gexp_leaderboard_task.before_loop
	async def before_lifetime_gexp_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_lifetime_gexp_leaderboard(self):
		logging.debug("Updating lifetime gexp leaderboard")
		# TODO: Only add players if they are currently in the guild

		cursor = self.local.cursor
		query = cursor.execute("""
			select uuid, SUM(amount) as total_gexp
			from expHistory
			group by uuid
			order by total_gexp desc
		""")
		results = query.fetchall()

		leaderboard_embed = discord.Embed(timestamp=datetime.datetime.now())
		leaderboard_data = []
		position = 1
		for line in results:
			uuid, amount = line[0], line[1]
			player_name = self.resolve_player_title(uuid)

			if position == 1:
				leaderboard_data.append(f":first_place:  {player_name}  -  {amount:,}")
			elif position == 2:
				leaderboard_data.append(f":second_place:  {player_name}  -  {amount:,}")
			elif position == 3:
				leaderboard_data.append(f":third_place:  {player_name}  -  {amount:,}")
				leaderboard_data.append(" ========== ")
			else:
				if amount != 0:
					leaderboard_data.append(f"#{position} {player_name} - {amount:,}")
			position = position + 1

		leaderboard_embed.title = "Lifetime GEXP Leaderboard"
		leaderboard_embed.description = "\n".join(leaderboard_data)
		await self.lb_lifetime_message.edit(embed=leaderboard_embed)

	@app_commands.command(name="update-lifetime-leaderboard", description="Force-update the lifetime gexp leaderboard (Admins Only")
	async def update_lifetime_gexp_leaderboard_command(self, interaction: discord.Interaction) -> None:
		has_permission = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permission:
			return

		logging.debug("Force-updating lifetime gexp leaderboard...")
		await interaction.response.defer()
		start_time = time.perf_counter()
		await self.update_lifetime_gexp_leaderboard()
		end_time = time.perf_counter()
		response_embed = discord.Embed()
		response_embed.colour = discord.Colour(0x08a169)
		response_embed.description = f"Finished in f{end_time - start_time} seconds"
		await interaction.edit_original_response(embed=response_embed)

	@tasks.loop(hours=2)
	async def yearly_gexp_leaderboard_task(self) -> None:
		if not self.has_run_yearly:
			self.has_run_yearly = True
			logging.info("LeaderboardUpdater: Skipping first run (yearly)")
			return
		logging.info("LeaderboardUpdater: Running Yearly GEXP Task")
		await self.update_yearly_gexp_leaderboard()

	@yearly_gexp_leaderboard_task.before_loop
	async def before_yearly_gexp_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_yearly_gexp_leaderboard(self):
		logging.debug("Updating yearly gexp leaderboard")
		# TODO: Only add players if they are currently in the guild

		cursor = self.local.cursor
		query = cursor.execute("""
				select uuid, SUM(amount) as total_gexp
				from expHistory
				where timestamp >= strftime('%s', date('now', 'start of year'))
				group by uuid
				order by total_gexp desc
			""")
		results = query.fetchall()

		leaderboard_embed = discord.Embed(timestamp=datetime.datetime.now())
		leaderboard_data = []
		position = 1
		for line in results:
			uuid, amount = line[0], line[1]
			player_name = self.resolve_player_title(uuid)

			if position == 1:
				leaderboard_data.append(f":first_place:  {player_name}  -  {amount:,}")
			elif position == 2:
				leaderboard_data.append(f":second_place:  {player_name}  -  {amount:,}")
			elif position == 3:
				leaderboard_data.append(f":third_place:  {player_name}  -  {amount:,}")
				leaderboard_data.append(" ========== ")
			else:
				if amount != 0:
					leaderboard_data.append(f"#{position} {player_name} - {amount:,}")
			position = position + 1

		leaderboard_embed.title = "Yearly GEXP Leaderboard"
		leaderboard_embed.description = "\n".join(leaderboard_data)
		await self.lb_yearly_message.edit(embed=leaderboard_embed)

	@app_commands.command(name="update-yearly-leaderboard",
	                      description="Force-update the yearly gexp leaderboard (Admins Only")
	async def update_yearly_gexp_leaderboard_command(self, interaction: discord.Interaction) -> None:
		has_permission = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permission:
			return

		logging.debug("Force-updating yearly gexp leaderboard...")
		await interaction.response.defer()
		start_time = time.perf_counter()
		await self.update_yearly_gexp_leaderboard()
		end_time = time.perf_counter()
		response_embed = discord.Embed()
		response_embed.colour = discord.Colour(0x08a169)
		response_embed.description = f"Finished in f{end_time - start_time} seconds"
		await interaction.edit_original_response(embed=response_embed)

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
		finished_lifetime_gexp_leaderboard = await self.update_lifetime_gexp_leaderboard()

		yearly_lb_message = await self.lb_channel.send(
			embed=discord.Embed(title="This is the yearly gexp leaderboard"))
		self.config.set_setting("lb_yearly_gexp_id", f"{yearly_lb_message.id}")
		finished_yearly_gexp_leaderboard = await self.update_yearly_gexp_leaderboard()

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

	def resolve_player_title(self, uuid) -> str:
		discord_link = self.local.discord_link.get_link(uuid)
		if discord_link:
			discord_member = self.bot.get_guild(self.server_id).get_member(int(discord_link.discord_id))
			player_name = discord_member.mention if discord_member else None
		else:
			player_data = self.local.uuid_cache.get_player(uuid)
			if player_data:
				player_name = player_data.name
			else:
				player_name = util.mcign.MCIGN(util.mcign.dash_uuid(uuid=uuid)).name
				timestamp = datetime.datetime.now().timestamp()
				self.local.uuid_cache.add_player(uuid, player_name, timestamp)
		if player_name:
			player_name = player_name.replace('_', '\\_')
		return player_name


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: LeaderboardUpdater")
	await bot.add_cog(LeaderboardUpdater(bot))
