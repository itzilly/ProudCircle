import json
import time
import uuid

import discord
import logging

from datetime import datetime
from discord import app_commands
from discord.ext import commands, tasks

from util import local, embed_lib, log_link
from util.local import XP_DIVISION_DATA_PATH


def rgb_to_decimal(r, g, b):
	return (r << 16) + (g << 8) + b


class DivisionRoleUpdater(commands.Cog):
	def __init__(self, bot: commands.Bot, *args, **kwargs):
		super().__init__(*args, **kwargs)

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
		self.has_run = False
		self.is_running = False

	def get_member_xp(self, member):
		cmd = "SELECT uuid, amount FROM expHistory ORDER BY date DESC"

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
			logging.error(f"Discord member ({discord_link.discord_id}) not found, please view latest log file for more details")
			logging.debug(f"link.row_id : {discord_link.row_id}")
			logging.debug(f"link.uuid : {discord_link.uuid}")
			logging.debug(f"link.discord_id : {discord_link.discord_id}")
			logging.debug(f"link.discord_username: {discord_link.discord_username}")
			logging.debug(f"link.linked_at: {discord_link.linked_at}")
			self.errors = self.errors + 1
			return

		# Add the <-- GEXP --> Cosmetic role (cosmetic role id: 1055844799015563274)
		cosmetic_role_id = 1055844799015563274
		if self.bot.get_guild(self.server_id).get_role(cosmetic_role_id) not in discord_member.roles:
			logging.debug(f"Adding cosmetic role to {discord_member.name}")
			await discord_member.add_roles(self.bot.get_guild(self.server_id).get_role(cosmetic_role_id))

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

		with open(XP_DIVISION_DATA_PATH, encoding='utf-8') as json_file:
			roles_data = json.load(json_file)

		cmd = "SELECT DISTINCT uuid FROM expHistory"
		table_members = self.cursor.execute(cmd).fetchall()

		for role in roles_data["roles"]:
			self.all_division_role_ids.append(role["role_id"])

		for member in table_members:
			try:
				await self.update_member_division(member)
			except Exception as e:
				logging.critical(e)

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


async def setup(bot: commands.Bot):
	logging.debug("Adding cog: DivisionRoleUpdater")
	await bot.add_cog(DivisionRoleUpdater(bot))
