import json
import time
import asyncio
import logging
import aiohttp
import discord
import datetime

import requests

import util.mcign

from discord import app_commands
from util import local, embed_lib
from discord.ext import tasks, commands
from util.local import XP_DIVISION_DATA_PATH
from util.command_helper import ensure_bot_permissions


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

		self.lb_monthly_message = await self.lb_channel.fetch_message(int(self.lb_monthly_message_id))
		if self.lb_monthly_message is not None:
			logging.debug("Activating Monthly Gexp Leaderboard Task")
			self.monthly_gexp_leaderboard_task.start()

		self.lb_weekly_message = await self.lb_channel.fetch_message(int(self.lb_weekly_message_id))
		if self.lb_weekly_message is not None:
			logging.debug("Activating Weekly Gexp Leaderboard Task")
			self.weekly_gexp_leaderboard_task.start()

		self.lb_daily_message = await self.lb_channel.fetch_message(int(self.lb_daily_message_id))
		if self.lb_daily_message is not None:
			logging.debug("Activating Daily GEXP Leaderboard Task")
			self.daily_gexp_leaderboard_task.start()

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
				# highest_role_mention = self.lb_channel.guild.get_role(player["highest_division"]["role_id"]).mention
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
		cmd = """
		select uuid, SUM(amount) as total_gexp
		from expHistory
		group by uuid
		order by total_gexp desc
		"""

		leaderboard_embed = discord.Embed(
			timestamp=datetime.datetime.now(),
			title="Lifetime GEXP Leaderboard",
			# colour=discord.Colour()
		)
		leaderboard_embed = await self.construct_leaderboard(leaderboard_embed, cmd)
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
		cmd = """
			select uuid, SUM(amount) as total_gexp
			from expHistory
			where timestamp >= strftime('%s', date('now', 'start of year'))
			group by uuid
			order by total_gexp desc
		"""

		leaderboard_embed = discord.Embed(
			timestamp=datetime.datetime.now(),
			title="Yearly GEXP Leaderboard",
			# colour=discord.Colour()
		)
		leaderboard_embed = await self.construct_leaderboard(leaderboard_embed, cmd)
		await self.lb_yearly_message.edit(embed=leaderboard_embed)

	@tasks.loop(hours=2)
	async def monthly_gexp_leaderboard_task(self) -> None:
		if not self.has_run_monthly:
			self.has_run_monthly = True
			logging.info("LeaderboardUpdater: Skipping first run (monthly)")
			return
		logging.info("LeaderboardUpdater: Running Monthly GEXP Task")
		await self.update_monthly_gexp_leaderboard()

	@monthly_gexp_leaderboard_task.before_loop
	async def before_monthly_gexp_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_monthly_gexp_leaderboard(self):
		logging.debug("Updating monthly gexp leaderboard")
		cmd = """
			select uuid, SUM(amount) as total_gexp
			from expHistory
			where timestamp >= strftime('%s', date('now', 'start of month', 'localtime')) * 1000
			group by uuid
			order by total_gexp desc
		"""
		leaderboard_embed = discord.Embed(
			timestamp=datetime.datetime.now(),
			title="Monthly GEXP Leaderboard",
			# colour=discord.Colour()
		)
		leaderboard_embed = await self.construct_leaderboard(leaderboard_embed, cmd)
		await self.lb_monthly_message.edit(embed=leaderboard_embed)

	@app_commands.command(name="update-monthly-leaderboard", description="Force-update the monthly gexp leaderboard (Admins Only")
	async def update_monthly_gexp_leaderboard_command(self, interaction: discord.Interaction) -> None:
		has_permission = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permission:
			return

		logging.debug("Force-updating monthly gexp leaderboard...")
		await interaction.response.defer()
		start_time = time.perf_counter()
		await self.update_monthly_gexp_leaderboard()
		end_time = time.perf_counter()
		response_embed = discord.Embed()
		response_embed.colour = discord.Colour(0x08a169)
		response_embed.description = f"Finished in f{end_time - start_time} seconds"
		await interaction.edit_original_response(embed=response_embed)

	@app_commands.command(name="update-yearly-leaderboard", description="Force-update the yearly gexp leaderboard (Admins Only")
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

	@tasks.loop(hours=2)
	async def weekly_gexp_leaderboard_task(self) -> None:
		if not self.has_run_weekly:
			self.has_run_weekly = True
			logging.info("LeaderboardUpdater: Skipping first run (weekly)")
			return
		logging.info("LeaderboardUpdater: Running weekly GEXP Task")
		await self.update_weekly_gexp_leaderboard()

	@weekly_gexp_leaderboard_task.before_loop
	async def before_weekly_gexp_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_weekly_gexp_leaderboard(self):
		logging.debug("Updating weekly gexp leaderboard")
		cmd = """
			select uuid, SUM(amount) as total_gexp
			from expHistory
			where date(timestamp, 'unixepoch', 'weekday 1', '-6 day') = date('now', 'weekday 1', '-6 day')
			group by uuid
			order by total_gexp desc
		"""
		leaderboard_embed = discord.Embed(
			timestamp=datetime.datetime.now(),
			title="Weekly GEXP Leaderboard",
			# colour=discord.Colour()
		)
		leaderboard_embed = await self.construct_leaderboard(leaderboard_embed, cmd)
		await self.lb_weekly_message.edit(embed=leaderboard_embed)

	@app_commands.command(name="update-weekly-leaderboard", description="Force-update the weekly gexp leaderboard (Admins Only)")
	async def update_weekly_gexp_leaderboard_command(self, interaction: discord.Interaction) -> None:
		has_permission = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permission:
			return

		logging.debug("Force-updating weekly gexp leaderboard...")
		await interaction.response.defer()
		start_time = time.perf_counter()
		await self.update_weekly_gexp_leaderboard()
		end_time = time.perf_counter()
		response_embed = discord.Embed()
		response_embed.colour = discord.Colour(0x08a169)
		response_embed.description = f"Finished in f{end_time - start_time} seconds"
		await interaction.edit_original_response(embed=response_embed)

	@tasks.loop(minutes=15)
	async def daily_gexp_leaderboard_task(self) -> None:
		if not self.has_run_daily:
			self.has_run_daily = True
			logging.info("LeaderboardUpdater: Skipping first run (daily)")
			return
		logging.info("LeaderboardUpdater: Running daily GEXP Task")
		await self.update_daily_gexp_leaderboard()

	@daily_gexp_leaderboard_task.before_loop
	async def before_daily_gexp_leaderboard_task(self) -> None:
		await self.bot.wait_until_ready()

	async def update_daily_gexp_leaderboard(self) -> None:
		logging.debug("Updating daily gexp leaderboard")
		cmd = """
			SELECT uuid, SUM(amount) AS total_gexp
			FROM expHistory
			WHERE date = DATE('now')
			GROUP BY uuid
			ORDER BY total_gexp DESC;
		"""
		leaderboard_embed = discord.Embed(
			timestamp=datetime.datetime.now(),
			title="Daily GEXP Leaderboard",
			# colour=discord.Colour()
		)
		leaderboard_embed = await self.construct_leaderboard(leaderboard_embed, cmd)
		await self.lb_daily_message.edit(embed=leaderboard_embed)

	@app_commands.command(name="update-daily-leaderboard", description="Force-update the daily gexp leaderboard (Admins Only)")
	async def update_daily_gexp_leaderboard_command(self, interaction: discord.Interaction) -> None:
		has_permission = await ensure_bot_permissions(interaction, send_deny_response=True)
		if not has_permission:
			return

		logging.debug("Force-updating daily gexp leaderboard...")
		await interaction.response.defer()
		start_time = time.perf_counter()
		await self.update_daily_gexp_leaderboard()
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

		try:
			self.lb_division_message = await self.lb_channel.send(
				embed=discord.Embed(title="This is the division leaderboard"))
			self.config.set_setting("lb_division_id", f"{self.lb_division_message.id}")
			finished_division_leaderboard = await self.update_division_leaderboard()
		except Exception as e:
			logging.critical(f"Error generating division leaderboard: {e}")

		try:
			self.lb_lifetime_message = await self.lb_channel.send(
				embed=discord.Embed(title="This is the lifetime gexp leaderboard"))
			self.config.set_setting("lb_lifetime_gexp_id", f"{self.lb_lifetime_message.id}")
			finished_lifetime_gexp_leaderboard = await self.update_lifetime_gexp_leaderboard()
		except Exception as e:
			logging.critical(f"Error generating lifetime leaderboard: {e}")

		try:
			self.lb_yearly_message = await self.lb_channel.send(
				embed=discord.Embed(title="This is the yearly gexp leaderboard"))
			self.config.set_setting("lb_yearly_gexp_id", f"{self.lb_yearly_message.id}")
			finished_yearly_gexp_leaderboard = await self.update_yearly_gexp_leaderboard()
		except Exception as e:
			logging.critical(f"Error generating yearly leaderboard: {e}")

		try:
			self.lb_monthly_message = await self.lb_channel.send(
				embed=discord.Embed(title="This is the monthly gexp leaderboard"))
			self.config.set_setting("lb_monthly_gexp_id", f"{self.lb_monthly_message.id}")
			finished_monthly_gexp_leaderboard = await self.update_monthly_gexp_leaderboard()
		except Exception as e:
			logging.critical(f"Error generating monthly leaderboard: {e}")

		try:
			self.lb_weekly_message = await self.lb_channel.send(
				embed=discord.Embed(title="This is the weekly gexp leaderboard"))
			self.config.set_setting("lb_weekly_gexp_id", f"{self.lb_weekly_message.id}")
			finished_weekly_gexp_leaderboard = await self.update_weekly_gexp_leaderboard()
		except Exception as e:
			logging.critical(f"Error generating weekly leaderboard: {e}")

		try:
			self.lb_daily_message = await self.lb_channel.send(
				embed=discord.Embed(title="This is the daily gexp leaderboard"))
			self.config.set_setting("lb_daily_gexp_id", f"{self.lb_daily_message.id}")
			finished_daily_gexp_leaderboard = await self.update_daily_gexp_leaderboard()
		except Exception as e:
			logging.critical(f"Error generating daily leaderboard: {e}")

		finished_embed = discord.Embed()
		finished_embed.description = "Created leaderboards!"
		await interaction.followup.send(embed=finished_embed)

	async def construct_leaderboard(self, leaderboard_embed: discord.Embed, sql_command: str) -> discord.Embed:
		cursor = self.local.cursor
		query = cursor.execute(sql_command)
		results = query.fetchall()

		key = self.config.get_setting("api_key")
		guild_id = self.config.get_setting("guild_id")
		guild_url = f"https://api.hypixel.net/guild?key={key}&id={guild_id}"
		data = requests.get(guild_url)
		json_data = data.json()
		guild_members = json_data["guild"]["members"]
		members_list = [member["uuid"] for member in guild_members]

		leaderboard_data = []
		position = 1
		for line in results:
			uuid, amount = line[0], line[1]
			if uuid not in members_list:
				continue

			player_name = await self.resolve_player_title(uuid)

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
		leaderboard_embed.description = "\n".join(leaderboard_data)
		return leaderboard_embed

	async def resolve_player_title(self, uuid) -> str:
		discord_link = self.local.discord_link.get_link(uuid)
		if discord_link:
			discord_member = self.bot.get_guild(self.server_id).get_member(int(discord_link.discord_id))
			player_name = discord_member.mention if discord_member else None
		else:
			player_data = self.local.uuid_cache.get_player(uuid)
			if player_data:
				player_name = player_data.name
			else:
				player_name = await self.request_player_name(util.mcign.dash_uuid(uuid=uuid))
				logging.info(f"uuid: {uuid} | type: {type(player_name)} | name: {player_name}")
				if player_name is None:
					player_name = await self.request_player_name(util.mcign.dash_uuid(uuid=uuid))
				timestamp = datetime.datetime.now().timestamp()
				self.local.uuid_cache.add_player(uuid, player_name, timestamp)
		if player_name:
			player_name = player_name.replace('_', '\\_')
		return player_name

	async def request_player_name(self, uuid):
		if len(uuid) < 17:
			url = f"https://api.mojang.com/users/profiles/minecraft/{uuid}"
		else:
			url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				data = await resp.json()
				name = data.get("name", None)
				if name is None:
					logging.debug(f"Player not found:\n\tResponse:\t{resp}\n\tData:\t{data}")
				return name


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: LeaderboardUpdater")
	await bot.add_cog(LeaderboardUpdater(bot))
