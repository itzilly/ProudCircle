import logging
import discord

from util import fs
from discord import app_commands
from discord.ext import commands


class ReloadCommands(commands.GroupCog, name="reload"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.command(name="all_extensions", description="Reloads all extensions", )
    async def promotion_task(self, interaction: discord.Interaction):
        ext = fs.get_all_extensions()
        for extension in ext:
            try:
                await self.bot.reload_extension(extension)
            except Exception as e:
                logging.error(f"There was an error loading extension '{extension}': {e}")
        # Sync app commands
        await self.bot.tree.sync()
        await interaction.response.send_message(f"Reloaded {len(ext)} extensions")


async def setup(bot) -> None:
    logging.debug("Adding cog: ReloadCommands")
    await bot.add_cog(ReloadCommands(bot))
