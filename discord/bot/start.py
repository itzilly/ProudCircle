import sys
import discord
import logging
import asyncio

from util import fs
from util import registers
from datetime import datetime
from discord.ext import commands


# The Proud Circle Discord Bot
class ProudCircleDiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info(f"Logged in as {self.user}")

    async def setup_hook(self) -> None:
        # Load all extensions: commands, events, tasks, etc
        ext = fs.get_all_extensions()
        for extension in ext:
            logging.debug(f"Loading extension: {extension}...")
            try:
                await self.load_extension(extension)
                logging.debug(f"Loaded extension!")
            except Exception as e:
                logging.error(f"There was an error loading extension '{extension}': {e}")
        # Sync app commands
        await self.tree.sync()


# Checkers for db and yaml files:
def check_files():
    pass


# Startup discord bot
async def main():
    # Setup logger
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)

    root_logger = logging.getLogger('root')
    root_logger.setLevel(logging.DEBUG)

    datetime_format = "%Y-%m-%d %H:%M:%S"
    formatter = '%(name)s [%(asctime)s %(levelname)s] %(message)s'
    logging.basicConfig(
        datefmt=datetime_format,
        format=formatter,
        handlers=[
            logging.FileHandler("./data/logs/discord.log"),
            logging.FileHandler("./data/logs/" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Generate, load, and check the config file
    # Note: Will NOT override existing config
    registers.Settings.load()
    config = registers.Settings.config
    if registers.Settings.check_token() is False:
        exit(2)

    # Loads all registries
    registers.load_all()

    # Bot Meta-data Setup
    bot_intents = discord.Intents.default()
    bot_intents.message_content = True
    bot_intents.members = True
    bot_pfx = commands.when_mentioned
    bot_description = "A Discord Bot for the Proud Circle Guild!"

    # Start the discord bot
    bot = ProudCircleDiscordBot(intents=bot_intents, command_prefix=bot_pfx, description=bot_description)
    token = config.get('bot').get('token')
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
