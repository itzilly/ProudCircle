import discord

from util.config_handler import Settings


def no_perm_embed():
    embed = discord.Embed(
        description=":x: You do not have permission to use this command! :x:",
        colour=discord.Colour(0xfa1195)
    )
    return embed


def guild_cmd_embed():
    embed = discord.Embed(
        description="Oh no, looks like you've used a slash command that is only accessible in a server! "
                    "Please don't use any commands in my dms, thanks!",
        colour=discord.Colour(0xfa1195)
    )
    return embed


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

    if level == "any-admin" or level == "any_admin" or level == "any":
        if bot_admin or discord_admin:
            return True
        return False

    return None


class CommandUser:
    def __init__(self, interaction_user):
        self.is_bot_admin = False
        if interaction_user.get_role(Settings.config['discord']['role_ids']['bot_admin']):
            self.is_bot_admin = True

        self.is_discord_staff = False
        if interaction_user.resolved_permissions.administrator:
            self.is_discord_staff = True

        self.is_admin = False
        if self.is_bot_admin or self.is_discord_staff:
            self.is_admin = True
