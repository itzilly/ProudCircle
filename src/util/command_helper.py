import logging
import util.local as fs

from util.embed_lib import *
from util.mcign import MCIGN


async def ensure_bot_permissions(interaction: discord.Interaction, send_deny_response=False):
	has_permission = False

	user = interaction.user

	logging.debug(f"Checking bot permissions for {user}")
	cmd = "SELECT bot_admin_role_id FROM config"
	request = fs.LOCAL_DATA.cursor.execute(cmd).fetchone()

	try:
		bot_role_id = int(request[0])
		if user.get_role(bot_role_id):
			logging.debug("Located role ID")
			has_permission = True
	except TypeError:
		logging.error("No bot token found")
		if send_deny_response:
			await interaction.response.send_message(embed=InsufficientPermissionsEmbed())
		return False

	if send_deny_response and not has_permission:
		await interaction.response.send_message(embed=InsufficientPermissionsEmbed())
	return has_permission


# def define_player_from_interaction(interaction: discord.Interaction):
# 	player = fs.LOCAL_DATA.uuid_cache.get_player(interaction.user.id)
# 	if player is None:
# 		timestamp = datetime.datetime.now().timestamp()
# 		player = MCIGN(player_id)
# 		self.local_data.uuid_cache.add_player(player.uuid, player.name, timestamp)
# 	return player
