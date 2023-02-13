import discord
import logging
import requests
import datetime

from util import local, mcign, embed_lib
from util.mcign import MCIGN
from discord import app_commands
from discord.ext import commands


how_to_link = discord.Embed(colour=discord.Colour(0xfa1195))
how_to_link.add_field(
    name="How to link your discord account on hypixel:",
    value="`#1` Go to any game lobby and right click on your head in your hotbar.\n"
          "`#2` In the GUI, select 'Social Media'. It looks like a twitter head.\n"
          "`#3` Left click the discord head in the new popup.\n"
          "`#4` Copy your discord username#number and paste in game chat!")


class LinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_player(self, player_id):
        player = local.LOCAL_DATA.uuid_cache.get_player(player_id)
        if player is None:
            timestamp = datetime.datetime.now().timestamp()
            player = MCIGN(player_id)
            local.LOCAL_DATA.uuid_cache.add_player(player.uuid, player.name, timestamp)
        return player

    @app_commands.command(name="link", description="Link your discord and minecraft account")
    @app_commands.describe(username="Your minecraft username to link!")
    async def link(self, interaction: discord.Interaction, username: str):
        # Make sure it's a valid username
        if not mcign.is_valid_minecraft_username(username) or mcign.is_valid_mojang_uuid(mcign.cleanup_uuid(username)):
            await interaction.response.send_message(embed=embed_lib.InvalidArgumentEmbed())
            return

        # Make sure their account isn't already linked
        link = local.LOCAL_DATA.discord_link.get_link(interaction.user.id)
        if link is not None:  # AKA Their account IS linked
            already_linked_embed = discord.Embed(colour=discord.Colour(0x820529))
            already_linked_embed.description = "You've already linked your account! If you need to unlink your discord " \
                                               "and minecraft account, use `/unlink`"
            await interaction.response.send_message(embed=already_linked_embed)
            return

        # Make API call to make sure username is linked to a valid Mojang account
        mojang_player = self.get_player(username)
        if mojang_player.uuid is None or mojang_player.name is None:
            await interaction.response.send_message(embed=embed_lib.InvalidMojangUserEmbed(player=username))
            return

        # Get hypixel player data
        key = local.LOCAL_DATA.config.get_setting("api_key")
        uuid = mojang_player.uuid
        player_data = requests.get("https://api.hypixel.net/player?key={}&uuid={}".format(key, uuid)).json()
        hypixel_discord_record = player_data.get('player', {}).get("socialMedia", {}).get("links").get("DISCORD", None)
        if hypixel_discord_record is None:
            logging.error(f"[linking] Player {mojang_player.uuid} does not contain hypixel discord record")
            await interaction.response.send_message(embed=embed_lib.ApiErrorEmbed())
            return

        # Check if the interaction user matches hypixel's records
        senders_discord_username = f"{interaction.user.name}#{interaction.user.discriminator}"
        if senders_discord_username != hypixel_discord_record:
            await interaction.response.send_message(embed=how_to_link)
            return

        # Everything worked out! Add the link
        discord_id = interaction.user.id
        local.LOCAL_DATA.discord_link.register_link(uuid, discord_id, senders_discord_username)
        successful_embed = embed_lib.SuccessfullyLinkedEmbed(mojang_player.name, interaction.user)
        await interaction.response.send_message(embed=successful_embed)


class UnlinkCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unlink", description="Unlink your discord and minecraft account")
    async def unlink(self, interaction: discord.Interaction):
        pass


# Add link and unlink commands to bot
async def setup(bot: commands.Bot):
    logging.debug("Adding cog: LinkCommand")
    await bot.add_cog(LinkCommand(bot))
    logging.debug("Adding Cog: UnlinkCommand")
    await bot.add_cog(UnlinkCommand(bot))
