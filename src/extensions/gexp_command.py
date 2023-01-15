import discord
import logging
import sqlite3
import datetime


from util import local, mcign
from util import embed_lib
from util.mcign import MCIGN
from discord.ext import commands
from discord import app_commands


class GexpCommand(commands.GroupCog, name="gexp"):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.local_data = local.LOCAL_DATA

	def define_player(self, interaction: discord.Interaction, player):
		pass

	@app_commands.command(name="daily", description="GEXP a player has earned today")
	@app_commands.describe(player="Player to get stats for")
	async def daily_command(self, interaction: discord.Interaction, player: str = None) -> None:
		log_message = f"User {interaction.user.id} ran command '/daily'"
		if player is not None:
			log_message = log_message + f" {player}"
		logging.debug(log_message)

		if player is None:
			discord_link = local.LOCAL_DATA.discord_link.get_link(interaction.user.id)
			player = discord_link.uuid

			if discord_link is None:
				await interaction.response.send_message(embed=embed_lib.InvalidArgumentEmbed())
				return

		mojang_player = self.get_player(player)
		player_uuid = mojang_player.uuid
		if player_uuid is None:
			await interaction.response.send_message(embed=embed_lib.InvalidMojangUserEmbed(player=player))
			return

		cursor = self.local_data.cursor
		date_today = datetime.datetime.today().strftime("%Y-%m-%d")
		cmd = "SELECT date, amount FROM expHistory WHERE (uuid = ?) AND (date = ?)"
		query = cursor.execute(cmd, (player_uuid, date_today))
		result = query.fetchone()
		if result is None:
			await interaction.response.send_message(embed=embed_lib.PlayerGexpDataNotFoundEmbed(player=mojang_player.name))
			return
		gexp_today = result[1]
		await interaction.response.send_message(embed=embed_lib.DailyGexpEmbed(mojang_player.name, player_uuid, result[1], result[0]))

	@app_commands.command(name="weekly", description="GEXP a player has earned in the last 7 days")
	@app_commands.describe(player="Player to get stats for")
	async def weekly_command(self, interaction: discord.Interaction, player: str = None) -> None:
		if player is None:
			discord_link = local.LOCAL_DATA.discord_link.get_link(interaction.user.id)
			player = discord_link.uuid

			if discord_link is None:
				await interaction.response.send_message(embed=embed_lib.InvalidArgumentEmbed())
				return

		mojang_player = self.get_player(player)
		player_uuid = mojang_player.uuid
		if player_uuid is None:
			await interaction.response.send_message(embed=embed_lib.InvalidMojangUserEmbed(player=player))
			return

		cursor = self.local_data.cursor

		# get the current date and 7 days ago
		current_date = datetime.datetime.today().strftime("%Y-%m-%d")
		seven_days_ago = (datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

		# create the query with the uuid, current_date and seven_days_ago
		cmd = f"SELECT date, amount FROM expHistory WHERE (uuid = ?) AND (date BETWEEN ? AND ?) ORDER BY date DESC"
		query = cursor.execute(cmd, (player_uuid, seven_days_ago, current_date))
		results = query.fetchall()
		weekly_data = {}
		for row in results:
			amount = row[1]
			date = row[0]
			weekly_data[date] = amount
		await interaction.response.send_message(embed=embed_lib.WeeklyGexpEmbed(
			player_name=mojang_player.name,
			player_uuid=mojang_player.uuid,
			gexp=weekly_data,
			todays_date=datetime.datetime.today()
		))

		# await interaction.response.send_message("You sent the weekly command!")

	@app_commands.command(name="monthly", description="GEXP a player has earned in the last month")
	@app_commands.describe(player="Player to get stats for")
	async def monthly_command(self, interaction: discord.Interaction, player: str = None) -> None:
		if player is None:
			discord_link = local.LOCAL_DATA.discord_link.get_link(interaction.user.id)
			player = discord_link.uuid

			if discord_link is None:
				await interaction.response.send_message(embed=embed_lib.InvalidArgumentEmbed())
				return

		mojang_player = self.get_player(player)
		player_uuid = mojang_player.uuid
		if player_uuid is None:
			await interaction.response.send_message(embed=embed_lib.InvalidMojangUserEmbed(player=player))
			return

		cursor = self.local_data.cursor

		# get the current date and first day of the current month
		current_date = datetime.datetime.today().strftime("%Y-%m-%d")
		first_day_of_month = datetime.datetime.today().replace(day=1).strftime("%Y-%m-%d")

		# create the query with the uuid, current_date and first_day_of_month
		cmd = f"SELECT date, amount FROM expHistory WHERE (uuid = ?) AND (date BETWEEN ? AND ?) ORDER BY date DESC"
		query = cursor.execute(cmd, (player_uuid, first_day_of_month, current_date))
		results = query.fetchall()
		monthly_data = {}
		for row in results:
			amount = row[1]
			date = row[0]
			monthly_data[date] = amount
		await interaction.response.send_message(embed=embed_lib.MonthlyGexpEmbed(
			player_name=mojang_player.name,
			player_uuid=mojang_player.uuid,
			gexp=monthly_data,
			todays_date=datetime.datetime.today()
		))

	@app_commands.command(name="yearly", description="GEXP a player has earned in the last year")
	@app_commands.describe(player="Player to get stats for")
	async def yearly_command(self, interaction: discord.Interaction, player: str = None) -> None:
		await interaction.response.send_message("You sent the yearly command!")

	@app_commands.command(name="lifetime", description="GEXP a player has earned since the beginning of 2023")
	@app_commands.describe(player="Player to get stats for")
	async def yearly_command(self, interaction: discord.Interaction, player: str = None) -> None:
		if player is None:
			discord_link = local.LOCAL_DATA.discord_link.get_link(interaction.user.id)
			player = discord_link.uuid

			if discord_link is None:
				await interaction.response.send_message(embed=embed_lib.InvalidArgumentEmbed())
				return

		mojang_player = self.get_player(player)
		player_uuid = mojang_player.uuid
		if player_uuid is None:
			await interaction.response.send_message(embed=embed_lib.InvalidMojangUserEmbed(player=player))
			return

		cursor = self.local_data.cursor
		query = cursor.execute("select SUM(amount) from expHistory where uuid is ?", (player_uuid, ))
		result = query.fetchone()[0]
		if result is None:
			await interaction.response.send_message(embed=embed_lib.PlayerGexpDataNotFoundEmbed(player=mojang_player.name))
			return
		lifetime_gexp = f"{result:,}"
		await interaction.response.send_message(embed=embed_lib.YearlyGexpEmbed(mojang_player.name, player_uuid, 1, result))
		# await interaction.response.send_message(lifetime_gexp)

	def get_player(self, player_id):
		player = self.local_data.uuid_cache.get_player(player_id)
		if player is None:
			timestamp = datetime.datetime.now().timestamp()
			player = MCIGN(player_id)
			self.local_data.uuid_cache.add_player(player.uuid, player.name, timestamp)
		return player


async def setup(bot) -> None:
	logging.debug("Adding cog: GexpCommand")
	await bot.add_cog(GexpCommand(bot))
