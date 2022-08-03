import discord
import logging
from discord import app_commands
from discord.ext import commands

from util import fs
from util import registers
from util.embed_builder import EmbedBuilder


discord_rules = """
[ :x: ]  Do not send ANY scam discord servers/links
[ :x: ]  Don't debate, discuss or mention any ongoing political topics or racistic/lgbt topics. You can say your opinion in DM's however we can not moderate private conversations.
[ :x: ]  Sending jumpscares, IP grabbers, etc is NOT allowed.
[ :x: ]  **NEVER** Ping guild/discord staff for no reason (This includes wasting time)!
[ :x: ]  Do not threaten discord members without fairness. Do not offend [swear on] anyone for no reason.
[ :x: ]  Spamming is not allowed and will NOT be taken lightly!
[ :x: ]  Sending any sexual/nsfw images or messages will be highly punished. NOT ALLOWED AT ALL!
[ :x: ]  Raids of any kind without previous discord staff approval is NOT tolerated! **YOU WILL BE __BANNED FOREVER__** *(That's a long time)*!
[ :x: ]  Everyone who Gatro doesn't recognize by your discord username MUST nickname to your ign!
[ :x: ]  Do not debate/talk back to/try to reason/argue with staff.
[ :x: ]  Don't be a dick, it's that simple!
"""



class SetupCommands(commands.GroupCog, name="setup"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="roles", description="Create all roles for the discord bot")
    async def create_all_roles(self, interaction: discord.Interaction) -> None:
    	subcommand_name = "/setup roles"
    	logging.debug(f"COMMANDS | User {interaction.user.id} ran command '{subcommand_name}'")

        # Permissions Check
        if not interaction.user.resolved_permissions.administrator:
            embed = discord.Embed(
                description=":x: You do not have permission to use this command! :x:",
                colour=discord.Colour(0xfa1195)
            )
            return await interaction.response.send_message(embed=embed)

        await interaction.response.send_message("Please wait while I create all roles...")

        # Check if the roles have already been created
        if registers.Settings.config['discord']['roles_have_been_created']:
            embed = discord.Embed(
                description="You cannot use this command more than once! The discord roles have already been created.",
                colour=discord.Colour(0xfa1195)
            )
            return await interaction.response.send_message(embed=embed)

        # Create Bot Admin Role
        bot_admin_role = await interaction.guild.create_role(
            name="Proud Circle Bot Admin",
            hoist=False,
            mentionable=False,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Discord Staff Role
        discord_staff_role = await interaction.guild.create_role(
            name="[ 📱 ] Discord staff",
            colour=discord.Colour(0x000001),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                manage_channels=True,
                manage_roles=True,
                view_audit_log=True,
                view_guild_insights=True,
                manage_webhooks=True,
                manage_guild=True,
                create_instant_invite=True,
                change_nickname=True,
                manage_nicknames=True,
                kick_members=True,
                ban_members=True,
                mute_members=True,
                create_public_threads=True,
                create_private_threads=True,
                embed_links=True,
                attach_files=True,
                add_reactions=True,
                use_external_emojis=True,
                mention_everyone=True,
                manage_messages=True,
                manage_threads=True,
                read_message_history=True,
                send_tts_messages=True,
                send_messages_in_threads=True,
                send_messages=True,
                use_application_commands=True,
                connect=True,
                speak=True,
                stream=True,
                use_embedded_activities=True,
                use_voice_activation=True,
                priority_speaker=True,
                deafen_members=True,
                move_members=True,
                request_to_speak=True,
                manage_events=True
            )
        )

        # Create Guild Staff Role
        guild_staff_role = await interaction.guild.create_role(
            name="[ 🔥 ] Guild staff",
            colour=discord.Colour(0x232890),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Guild Champion Role
        guild_champion_role = await interaction.guild.create_role(
            name="[ 🏆 ] Champion",
            colour=discord.Colour(0xd0c11f),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Guild Celestial Role
        guild_celestial_role = await interaction.guild.create_role(
            name="[ ❤️ ] Celestial",
            colour=discord.Colour(0x2aaabd),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Guild Legend Role
        guild_legend_role = await interaction.guild.create_role(
            name="[⭐] Legend",
            colour=discord.Colour(0x4a1272),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Guild Member Role
        guild_member_role = await interaction.guild.create_role(
            name="[ 🌹 ] Guild member",
            colour=discord.Colour(0x66ad31),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Discord Guest Role
        discord_guest_role = await interaction.guild.create_role(
            name="[  ✌ ] Guest",
            colour=discord.Colour(0xaa229c),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Create Verified Role
        verified_role = await interaction.guild.create_role(
            name="Verified!",
            colour=discord.Colour(0xffffff),
            hoist=True,
            mentionable=True,
            permissions=discord.Permissions(
                use_application_commands=True
            )
        )

        # Update configuration file with all role id's
        config = .Settings.config
        role_ids = config['discord']['role_ids']
        role_ids['bot_admin'] = bot_admin_role.id
        role_ids['discord_staff'] = discord_staff_role.id
        role_ids['guild_staff'] = guild_staff_role.id
        role_ids['guild_champion'] = guild_champion_role.id
        role_ids['guild_celestial'] = guild_celestial_role.id
        role_ids['guild_legend'] = guild_legend_role.id
        role_ids['guild_member'] = guild_member_role.id
        role_ids['discord_guest'] = discord_guest_role.id
        role_ids['verified'] = verified_role.id
        role_ids['everyone'] = interaction.user.roles[0]
        config['discord']['roles_have_been_created'] = True
        registers.Settings.update(config)

        # Inform user about the updates
        embed = discord.Embed(description="Created all roles!",
                              colour=discord.Colour(0xfa1195)
                              )
        embed.set_author(name="Proud Circle Bot")
        embed.add_field(name="Roles:", value=f"{bot_admin_role.mention} \n"
                                             f"{discord_staff_role.mention} \n"
                                             f"{guild_staff_role.mention} \n"
                                             f"{guild_champion_role.mention} \n"
                                             f"{guild_celestial_role.mention} \n"
                                             f"{guild_legend_role.mention} \n"
                                             f"{guild_member_role.mention} \n"
                                             f"{discord_guest_role.mention} \n"
                                             f"{verified_role.mention}")
        await interaction.response.send_message(embed=embed)
        # TODO: Fix Champion Role Color

    @app_commands.command(name="rules", description="Select channel for rules")
    async def setup_rules(self, interaction: discord.Interaction) -> None:
    	subcommand_name = "/setup rules"
    	logging.debug(f"COMMANDS | User {interaction.user.id} ran command '{subcommand_name}'")

        # Permissions Check
        if not interaction.user.get_role(registers.Settings.config['discord']['role_ids']['bot_admin']):
            embed = discord.Embed(
                description=":x:  You do not have permission to use this command!  :x:",
                colour=discord.Colour(0xfa1195)
            )
            return await interaction.response.send_message(embed=embed)

        # Update Config with rules channel ID
        config = registers.Settings.config
        channel_ids = config['discord']['channel_ids']
        channel_ids['rules'] = interaction.channel_id
        registers.Settings.update(config)

        # Response Embed
        embed = EmbedBuilder()
        embed.set_title("__Proud Discord Community Discord Rules__")
        embed.use_default_thumbnail = False
        embed.add_field(
            title="**Discord Rules**\n"
                  "Please read the rules before continuing\n"
                  "*Please note our guild is a serious place and unallowed behavior WILL be punished!*",
            field_data=discord_rules
        )
        embed.remove_author()
        embed.use_default_footer = False
        await interaction.response.send_message(embed=embed.build())

    @app_commands.command(name="verification", description="Select channel for verification")
    async def setup_verification(self, interaction: discord.Interaction) -> None:
    	subcommand_name = "/setup verification"
    	logging.debug(f"COMMANDS | User {interaction.user.id} ran command '{subcommand_name}'")

        # Permissions Check
        if not interaction.user.get_role(registers.Settings.config['discord']['role_ids']['bot_admin']):
            embed = discord.Embed(
                description=":x:  You do not have permission to use this command!  :x:",
                colour=discord.Colour(0xfa1195)
            )
            return await interaction.response.send_message(embed=embed)

        await interaction.response.send_message("Please wait while I setup verification...")

        # Make all channels invisible unless member is verified
        config = registers.Settings.config
        verified_role_id = config['discord']['role_ids']['verified']
        guild_member_role_id = config['discord']['role_ids']['guild_member']
        for channel in interaction.guild.channels:
            await channel.set_permissions(interaction.guild.default_role, view_channel=False)  # @everyone can't see
            await channel.set_permissions(interaction.guild.get_role(verified_role_id), view_channel=True)  # @verified can see
        verified_channel = await interaction.guild.create_text_channel(
            name="verification",
            reason="Create verified channel"
        )
        config['discord']['channel_ids']['verification'] = verified_channel.id
        await verified_channel.set_permissions(interaction.guild.default_role, view_channel=True)
        await verified_channel.set_permissions(interaction.guild.get_role(verified_role_id), view_channel=False)

    @app_commands.command(name="linking", description="Setup linking discord account with hypixel account")
    async def setup_linking(self, interaction: discord.Interaction) -> None:
    	subcommand_name = "/setup linking"
    	logging.debug(f"COMMANDS | User {interaction.user.id} ran command '{subcommand_name}'")

        # Permissions Check
        if not interaction.user.get_role(registers.Settings.config['discord']['role_ids']['bot_admin']):
            embed = discord.Embed(
                description=":x:  You do not have permission to use this command!  :x:",
                colour=discord.Colour(0xfa1195)
            )
            return await interaction.response.send_message(embed=embed)

        await interaction.response.send_message("This feature is not yet avalible!")





async def setup(bot: commands.Bot):
    logging.debug("Adding cog: SetupCommands")
    await bot.add_cog(SetupCommands(bot))
