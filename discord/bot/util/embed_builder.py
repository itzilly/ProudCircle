import pytz
import discord
from datetime import datetime


class EmbedBuilder:
    def __init__(self):
        self.embed = discord.Embed()
        self.embed.colour = discord.Colour(0xfa1195)
        self.files = []
        self.use_timestamp = True
        self.use_default_footer = True
        self.use_default_thumbnail = True

    def set_title(self, title: str):
        self.embed.title = title

    def set_description(self, description: str):
        self.embed.description = description

    def set_color(self, hex_int: int):
        self.embed.colour = discord.Colour(hex_int)

    def add_field(self, title: str, field_data: str):
        self.embed.add_field(name=title, value=field_data)

    @DeprecationWarning
    def use_default_thumbnail(self):
        self.files.append(discord.File("./bin/images/icon.png", filename="icon.png"))
        self.embed.set_thumbnail(url="attachment://icon.png")

    def remove_author(self):
        self.embed.remove_author()

    def build(self):
        if self.use_timestamp:
            timezone = pytz.timezone('EST')
            self.embed.timestamp = datetime.now(tz=timezone)
        if self.use_default_footer:
            self.files.append(discord.File("./bin/images/itzilly-icon.png", filename="itzilly-icon.png"))
            self.embed.set_footer(text="Made by illyum", icon_url="attachment://itzilly-icon.png")
        if self.use_default_thumbnail:
            self.files.append(discord.File("./bin/images/icon.png", filename="icon.png"))
            self.embed.set_thumbnail(url="attachment://icon.png")
        return self.embed

    def local_image(self, file_path, filename):
        self.files.append(discord.File(file_path, filename=filename))
        url = "attachment://" + filename
        return url

    def get_files(self):
        return self.files
