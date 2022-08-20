import pytz
import sqlite3
import logging
import discord
import requests

from util.mcign import MCIGN
from datetime import datetime
from util.config_handler import Settings
from util.linked_database import LinkedDatabase
from util.error_embeds import ApiErrorEmbed, ConfigErrorEmbed


class PromoteTask:
    def __init__(self):
        self.name = "Promotion Task"
        self.errored = False
        self.error_embed = None
        self.con = sqlite3.connect('./data/discord.db')

    async def run(self, interaction: discord.Interaction):
        logging.debug("Running task: Promotions")
        config = Settings.config
        api_key = config.get('hypixel', {}).get('api_key', None)
        if api_key is None:
            self.errored = True
            self.error_embed = ConfigErrorEmbed(error_message="No API key detected\nPlease contact my admin!")
            return False
        guild_id = config.get('hypixel', {}).get('guid_id', None)
        if guild_id is None:
            self.errored = True
            self.error_embed = ConfigErrorEmbed(error_message="No guild ID detected\nPlease contact my admin!")
            return False
        ids = config.get('discord', {}).get('role_ids', {})
        uri = "https://api.hypixel.net/guild?key={}&id={}".format(api_key, guild_id)
        api_request = requests.get(uri)
        request_json = api_request.json()
        if not request_json.get('success'):
            self.errored = True
            if request_json.get('reason', None) is None:
                self.error_embed = ApiErrorEmbed(error_message="Unknown Error (code: 5)")
                return False
            self.error_embed = ApiErrorEmbed(error_message=request_json.get('reason'))
            return False
        guild_members_list = request_json.get('guild', {}).get('members', [])
        total_leaderboard = []
        nonzero_leaderboard = []
        top_ten_leaderboard = []

        # Get everyone's gexp
        for member in guild_members_list:
            entry = {}
            uuid = member.get('uuid', None)
            weekly_gexp = 0
            for day, gexp in member.get('expHistory').items():
                weekly_gexp += gexp
            entry['uuid'] = uuid
            entry['weekly_gexp'] = weekly_gexp
            entry['exp_history'] = member.get('expHistory')
            total_leaderboard.append(entry)
            if weekly_gexp != 0:
                player = MCIGN(id=uuid)
                entry['name'] = player.name
                nonzero_leaderboard.append(entry)
        total_leaderboard = sorted(total_leaderboard, key=lambda data: data['weekly_gexp'], reverse=True)
        nonzero_leaderboard = sorted(nonzero_leaderboard, key=lambda data: data['weekly_gexp'], reverse=True)
        top_ten_leaderboard = nonzero_leaderboard[:10]
        response_embed = discord.Embed(title="Weekly GEXP Promotions!")
        if len(top_ten_leaderboard) == 0 or len(top_ten_leaderboard) < 10:
            self.errored = True
            response_embed.add_field(
                name="Error",
                value="An unknown error has occurred. For more information refer to task log: {}")
            self.error_embed = response_embed
            return False

        # Roles
        champion = interaction.guild.get_role(ids['guild_champion'])
        celestial = interaction.guild.get_role(ids['guild_celestial'])
        legend = interaction.guild.get_role(ids['guild_legend'])

        # Create response message
        position = 1
        promotions = []
        for member in top_ten_leaderboard:
            match position:
                case 1:
                    first_gexp = member.get('weekly_gexp')
                    first_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        first_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        first_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 2:
                    second_gexp = member.get('weekly_gexp')
                    second_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        second_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        second_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 3:
                    third_gexp = member.get('weekly_gexp')
                    third_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        third_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        third_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 4:
                    fourth_gexp = member.get('weekly_gexp')
                    fourth_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        fourth_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        fourth_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 5:
                    fifth_gexp = member.get('weekly_gexp')
                    fifth_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        fifth_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        fifth_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 6:
                    sixth_gexp = member.get('weekly_gexp')
                    sixth_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        sixth_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        sixth_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 7:
                    seventh_gexp = member.get('weekly_gexp')
                    seventh_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        seventh_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        seventh_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 8:
                    eighth_gexp = member.get('weekly_gexp')
                    eighth_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        eighth_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        eighth_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 9:
                    ninth_gexp = member.get('weekly_gexp')
                    ninth_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        ninth_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        ninth_playername = member.get('name').replace("_", "\\_")
                    position += 1
                case 10:
                    tenth_gexp = member.get('weekly_gexp')
                    tenth_playername = member.get('name')
                    command = f"SELECT discord_id FROM discord_link WHERE player_uuid IS {member.get('uuid')}"
                    execute = self.con.execute(command)
                    response = execute.fetchall()
                    if len(response) is not None:
                        tenth_playername = interaction.guild.get_member(response[0]).mention
                    else:
                        tenth_playername = member.get('name').replace("_", "\\_")
                    position += 1

        response_message = f"Here are the weekly promotions!\n\n" \
                           f"        {champion.mention}\n" \
                           f"-------------------------------\n" \
                           f"`#1`   **{first_playername}**: " + '{:,}'.format(first_gexp) + " GEXP\n" \
                           f"-------------------------------\n" \
                           f"\n" \
                           f"       {celestial.mention}\n" \
                           f"`#2` **{second_playername}**: " + '{:,}'.format(second_gexp) + " GEXP\n" \
                           f"`#3` **{third_playername}**: " + '{:,}'.format(third_gexp) + " GEXP\n" \
                           f"\n" \
                           f"       {legend.mention}\n" \
                           f"`#4` **{fourth_playername}** : " + '{:,}'.format(fourth_gexp) + " GEXP\n" \
                           f"`#5` **{fifth_playername}** : " + '{:,}'.format(fifth_gexp) + " GEXP\n" \
                           f"`#6` **{sixth_playername}** : " + '{:,}'.format(sixth_gexp) + " GEXP\n" \
                           f"`#7` **{seventh_playername}** : " + '{:,}'.format(seventh_gexp) + " GEXP\n" \
                           f"`#8` **{eighth_playername}** : " + '{:,}'.format(eighth_gexp) + " GEXP\n" \
                           f"`#9` **{ninth_playername}** : " + '{:,}'.format(ninth_gexp) + " GEXP\n" \
                           f"`#10` **{tenth_playername}** : " + '{:,}'.format(tenth_gexp) + " GEXP\n\n\n" \
                           f"Congratulations to everyone who achieved a rank!"

        response_value = f"        {champion.mention}\n" \
                         f"-------------------------------\n" \
                         f"`#1`   **{first_playername}**: " + '{:,}'.format(first_gexp) + " GEXP\n" \
                         f"-------------------------------\n" \
                         f"\n" \
                         f"       {celestial.mention}\n" \
                         f"`#2` **{second_playername}**: " + '{:,}'.format(second_gexp) + " GEXP\n" \
                         f"`#3` **{third_playername}**: " + '{:,}'.format(third_gexp) + " GEXP\n" \
                         f"\n" \
                         f"       {legend.mention}\n" \
                         f"`#4` **{fourth_playername}** : " + '{:,}'.format(fourth_gexp) + " GEXP\n" \
                         f"`#5` **{fifth_playername}** : " + '{:,}'.format(fifth_gexp) + " GEXP\n" \
                         f"`#6` **{sixth_playername}** : " + '{:,}'.format(sixth_gexp) + " GEXP\n" \
                         f"`#7` **{seventh_playername}** : " + '{:,}'.format(seventh_gexp) + " GEXP\n" \
                         f"`#8` **{eighth_playername}** : " + '{:,}'.format(eighth_gexp) + " GEXP\n" \
                         f"`#9` **{ninth_playername}** : " + '{:,}'.format(ninth_gexp) + " GEXP\n" \
                         f"`#10` **{tenth_playername}** : " + '{:,}'.format(tenth_gexp) + " GEXP\n\n\n" \
                         f"Congratulations to everyone who achieved a rank!"

        response_embed_files = []
        response_embed = discord.Embed(title="Weekly rank promotions!")
        response_embed.add_field(name="Ranks for week of {week1}-{week2}", value=response_value)
        response_embed.colour = discord.Colour(0xfa1195)
        response_embed.timestamp = datetime.now(tz=pytz.timezone('EST'))
        response_embed_files.append(discord.File("./data/images/itzilly-icon.png", filename="itzilly-icon.png"))
        response_embed.set_footer(text="Made by illyum", icon_url="attachment://itzilly-icon.png")

        # Demotions
        for user in interaction.guild.members:
            if champion in user.roles:
                await user.remove_roles(champion)
                logging.debug(f"Removed role @champion from {user.display_name}")

            if celestial in user.roles:
                await user.remove_roles(celestial)
                logging.debug(f"Removed role @celestial from {user.display_name}")

            if legend in user.roles:
                await user.remove_roles(legend)
                logging.debug(f"Removed role @legend from {user.display_name}")

        # Promotions
        for todo in promotions:
            await interaction.guild.get_member(todo.get('user_id')).add_roles(todo.get('role_id'))
        # await interaction.response.send_message(response_message)
        await interaction.response.send_message(embed=response_embed, files=response_embed_files)

        logging.debug("Finished task: Promotions")
        return True
