import json
import aiohttp
import discord
import logging
import util.local

from datetime import datetime
from discord import app_commands
from util import local, embed_lib
from discord.ext import commands, tasks
from util.local import XP_DIVISION_DATA_PATH


def rgb_to_decimal(r, g, b):
	return (r << 16) + (g << 8) + b


class DivisionRoleUpdater(commands.Cog):
	def __init__(self, bot: commands.Bot, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.local_data: util.local.LocalData = util.local.LOCAL_DATA
		self.bot = bot

		# self.role_data = local.LOCAL_DATA.xp_division_data
		self.cursor = local.LOCAL_DATA.cursor
		self.server_id = int(local.LOCAL_DATA.config.get_setting("server_id"))
		self.server = self.bot.get_guild(self.server_id)
		with open(XP_DIVISION_DATA_PATH, encoding='utf-8') as json_file:
			self.roles_data = json.load(json_file)
		self.all_division_role_ids = []

		self.members_updated = 0
		self.errors = 0
		self.has_run = True
		self.is_running = False

		self.cosmetic_role_id = 1055844799015563274
		self.update_divisions_task.start()

	async def strip_member_of_divisions(self, member):
		uuid = member[0]
		discord_link = self.local_data.discord_link.get_link(uuid)
		if discord_link is None:
			self.errors = self.errors + 1
			return

		discord_member = await self.bot.get_guild(self.server_id).get_member(discord_link.discord_id)
		for role in self.roles_data:
			role_id = role["role_id"]
			for member_role in discord_member.roles:
				if member_role.id == role_id:
					logging.debug(f"Removing {member_role.name} from {discord_link.discord_username}")
				# await discord_member.remove_roles([discord.Object(role_id)])

		logging.debug(f"Removing cosmetic role from {discord_link.discord_username}")
		await discord_member.remove_roles([discord.Object(self.cosmetic_role_id)])

	async def update_member_division(self, member):
		uuid = member[0]
		cmd = "SELECT SUM(amount) FROM expHistory WHERE uuid IS ?"
		amount_query = self.cursor.execute(cmd, (uuid,)).fetchone()
		amount = int(amount_query[0])

		discord_link = local.LOCAL_DATA.discord_link.get_link(uuid)
		if discord_link is None:
			return
		discord_member = self.bot.get_guild(self.server_id).get_member(discord_link.discord_id)
		if discord_member is None:
			logging.error(
				f"Discord member ({discord_link.discord_id}) not found, please view latest log file for more details")
			logging.debug(f"link.row_id : {discord_link.row_id}")
			logging.debug(f"link.uuid : {discord_link.uuid}")
			logging.debug(f"link.discord_id : {discord_link.discord_id}")
			logging.debug(f"link.discord_username: {discord_link.discord_username}")
			logging.debug(f"link.linked_at: {discord_link.linked_at}")
			self.errors = self.errors + 1
			return

		# Add the <-- GEXP --> Cosmetic role (cosmetic role id: 1055844799015563274)
		if self.bot.get_guild(self.server_id).get_role(self.cosmetic_role_id) not in discord_member.roles:
			logging.debug(f"Adding cosmetic role to {discord_member.name}")
			await discord_member.add_roles(self.bot.get_guild(self.server_id).get_role(self.cosmetic_role_id))

		# Find the highest role the member qualifies for
		highest_role = None
		for role in self.roles_data["roles"]:
			if amount >= role["required_amount"]:
				if highest_role is None or role["required_amount"] > highest_role["required_amount"]:
					highest_role = role
		logging.debug(f"Adding role_id: {highest_role} | {discord_link.discord_id}")
		given_role = self.bot.get_guild(self.server_id).get_role(highest_role["role_id"])

		# Only update roles if the member does not already have the correct role
		if given_role not in discord_member.roles:
			logging.debug(f"Promoting {discord_member.name} to {given_role.name}")
			self.members_updated = self.members_updated + 1
			await discord_member.add_roles(given_role)

		# Remove all lower roles from the member
		if highest_role is not None:
			for role in discord_member.roles:
				if role.id in self.all_division_role_ids and role.id != highest_role["role_id"]:
					remove_role = self.bot.get_guild(self.server_id).get_role(role.id)
					logging.debug(f"Removing role_id: {role.id} | {discord_link.discord_id}")
					await discord_member.remove_roles(remove_role)

	async def run(self):
		if self.is_running:
			logging.warning("DivisionRoleUpdater: Attempted to run while already running")
			return

		self.is_running = True
		self.members_updated = 0
		self.errors = 0

		cmd = "SELECT DISTINCT uuid FROM expHistory"
		table_members = self.cursor.execute(cmd).fetchall()

		for role in self.roles_data["roles"]:
			self.all_division_role_ids.append(role["role_id"])

		guild_members = await self.fetch_guild_members_list()

		for member in table_members:
			member_uuid = member[0]
			if member_uuid not in guild_members:
				try:
					await self.strip_member_of_divisions(member)
				except Exception as e:
					self.errors = self.errors + 1
					logging.critical(e)
				continue

			try:
				await self.update_member_division(member)
			except Exception as e:
				logging.critical(e)
				self.errors = self.errors + 1

		self.is_running = False
		logging.info("Completed updating divisions!")

	@app_commands.command(name="update-divisions", description="Run the divisions update task")
	async def update_divisions_command(self, interaction: discord.Interaction):
		is_bot_admin = self.check_permission(interaction.user)
		if not is_bot_admin:
			await interaction.response.send_message(embed=embed_lib.InsufficientPermissionsEmbed())
			return

		await interaction.response.defer()
		await self.run()

		finished_embed = discord.Embed(
			timestamp=datetime.now(),
			title="Run Completion",
			description="Updated Divisions",
			colour=discord.Colour(0x4d18d6),
		)
		finished_embed.add_field(name="Members Updated:", value=f"{self.members_updated}")
		finished_embed.add_field(name="Handled Errors:", value=f"{self.errors}")
		await interaction.edit_original_response(embed=finished_embed)

	@tasks.loop(hours=2)
	async def update_divisions_task(self):
		if not self.has_run:
			self.has_run = True
			logging.debug("DivisionRoleUpdater: Skipping first run")
			return
		await self.run()

		finished_embed = discord.Embed(
			timestamp=datetime.now(),
			title="Run Completion",
			description="Updated Divisions",
			colour=discord.Colour(0x4d18d6),
		)
		finished_embed.add_field(name="Members Updated:", value=f"{self.members_updated}")
		finished_embed.add_field(name="Handled Errors:", value=f"{self.errors}")
		bot_log_channel_id = 1061815307473268827
		await self.bot.get_guild(self.server_id).get_channel(bot_log_channel_id).send_message(finished_embed)

	@update_divisions_task.before_loop
	async def before_update_divisions_task(self):
		await self.bot.wait_until_ready()

	# Permissions Check
	def check_permission(self, user: discord.Interaction.user):
		request = local.LOCAL_DATA.cursor.execute("SELECT bot_admin_role_id FROM config").fetchone()[0]
		if request is None:
			return False
		if user.get_role(int(request)):
			return True
		return False

	async def fetch_guild_members_list(self):
		key = self.local_data.config.get_setting("api_key")
		guild_id = self.local_data.config.get_setting("guild_id")
		url = f"https://api.hypixel.net/guild?key={key}&id={guild_id}"
		members_list = []
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				# ratelimit_remaining = response.headers["RateLimit-Remaining"]
				guild_data = await response.json()
				if not guild_data["success"]:
					logging.fatal(f"Unsuccessful in scraping api data: {response.headers} | {guild_data}")
					return None
				for member in guild_data.get("members", []):
					members_list.append(member.get("uuid", ""))
				return members_list


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: DivisionRoleUpdater")
	await bot.add_cog(DivisionRoleUpdater(bot))
