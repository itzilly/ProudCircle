import discord


class ApiErrorEmbed(discord.Embed):
    def __init__(self, error_message=None):
        super().__init__()
        self.colour = discord.Colour(0xf00c27)
        self.title = "Error Report: "
        if error_message is None:
            error_message = "Unknown Error, please refer to the latest `discord.log` file for more details."
        self.add_field(name="An API error has occurred:", value=error_message)


class ConfigErrorEmbed(discord.Embed):
    def __init__(self, error_message=None):
        super().__init__()
        self.colour = discord.Colour(0xf00c27)
        self.title = "Error Report: "
        if error_message is None:
            error_message = "Unknown Error, please refer to the latest `discord.log` file for more details."
        self.add_field(name="A configuration error has occurred:", value=error_message)
