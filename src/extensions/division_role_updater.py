import json
import discord
import logging

from util import local, embed_lib
from discord import app_commands
from discord.ext import commands

from util.local import XP_DIVISION_DATA_PATH


class DivisionRoleUpdater(commands.Cog):
	def __init__(self, bot: commands.Bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot
		# self.role_data = local.LOCAL_DATA.xp_division_data
		self.cursor = local.LOCAL_DATA.cursor

	def get_member_xp(self, member):
		cmd = "SELECT uuid, amount FROM expHistory ORDER BY date DESC"

	async def run(self, interaction):
		server_id = int(local.LOCAL_DATA.config.get_setting("server_id"))
		server = self.bot.get_guild(server_id)

		with open(XP_DIVISION_DATA_PATH, encoding='utf-8') as json_file:
			roles_data = json.load(json_file)

		cmd = "SELECT DISTINCT uuid FROM expHistory"
		table_members = self.cursor.execute(cmd).fetchall()

		all_division_role_ids = []
		for role in roles_data["roles"]:
			all_division_role_ids.append(role["role_id"])

		for member in table_members:
			uuid = member[0]
			cmd = "SELECT SUM(amount) FROM expHistory WHERE uuid IS ?"
			amount_query = self.cursor.execute(cmd, (uuid,)).fetchone()
			amount = int(amount_query[0])

			discord_link = local.LOCAL_DATA.discord_link.get_link(uuid)
			if discord_link is None:
				continue
			discord_member = self.bot.get_guild(server_id).get_member(discord_link.discord_id)

			# Find the highest role the member qualifies for
			highest_role = None
			for role in roles_data["roles"]:
				if amount >= role["required_amount"]:
					if highest_role is None or role["required_amount"] > highest_role["required_amount"]:
						highest_role = role
			logging.debug(f"Adding role_id: {highest_role} | {discord_link.discord_id}")
			given_role = self.bot.get_guild(server_id).get_role(highest_role["role_id"])
			await discord_member.add_roles(given_role)

			# Remove all lower roles from the member
			if highest_role is not None:
				for role in discord_member.roles:
					if role.id in all_division_role_ids and role.id != highest_role["role_id"]:
						remove_role = self.bot.get_guild(server_id).get_role(role.id)
						logging.debug(f"Removing role_id: {role.id} | {discord_link.discord_id}")
						await discord_member.remove_roles(remove_role)
					if self.bot.get_guild(server_id).get_role(1055844799015563274) not in discord_member.roles:
						await discord_member.add_roles(self.bot.get_guild(server_id).get_role(1055844799015563274))

	@app_commands.command(name="update-divisions", description="Run the divisions update task")
	async def update_divisions_command(self, interaction: discord.Interaction):
		is_bot_admin = self.check_permission(interaction.user)
		if not is_bot_admin:
			await interaction.response.send_message(embed=embed_lib.InsufficientPermissionsEmbed())
			return

		working_embed = discord.Embed(description="Running divisions task", colour=discord.Colour(0x1bb9cc))
		await interaction.response.send_message(embed=working_embed)
		await self.run(interaction)

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
