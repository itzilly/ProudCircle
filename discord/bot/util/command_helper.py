import discord

from util.config_handler import Settings


# Permissions Check
def check_permission(user: discord.Interaction.user, level: str):
    bot_admin = False
    if user.get_role(Settings.config['discord']['role_ids']['bot_admin']):
        bot_admin = True

    discord_admin = False
    if user.resolved_permissions.administrator:
        discord_admin = True

    if level == "bot-admin" or "bot_admin":
        return bot_admin

    if level == "discord-admin" or "discord_admin":
        return discord_admin

    if level == "any-admin" or "any_admin":
        if bot_admin or discord_admin:
            return True
        return False

    return None
