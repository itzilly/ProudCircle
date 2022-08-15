import sys
import discord
import logging
import asyncio

from util import fs
from datetime import datetime
from discord.ext import commands
from util.config_handler import Settings


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
            try:
                await self.load_extension(extension)
            except Exception as e:
                logging.error(f"There was an error loading extension '{extension}': {e}")
        # Sync app commands
        await self.tree.sync()


# Startup discord bot
async def main():
    # Setup logger
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)

    root_logger = logging.getLogger('root')
    root_logger.setLevel(logging.DEBUG)

    requests_logger = logging.getLogger('urllib3')
    requests_logger.setLevel(logging.INFO)

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

    # Generate and load all configuration files
    # (this includes json databases)
    fs.load_files()

    # Bot Meta-data Setup
    bot_intents = discord.Intents.default()
    bot_intents.message_content = True
    bot_intents.members = True
    bot_intents.guilds = True
    bot_intents.reactions = True
    bot_pfx = commands.when_mentioned
    bot_description = "A Discord Bot for the Proud Circle Guild!"

    # Start the discord bot
    bot = ProudCircleDiscordBot(intents=bot_intents, command_prefix=bot_pfx, description=bot_description)
    token = Settings.config.get('bot', {}).get('token', None)
    if token is None:
        logging.critical("No bot token detected! Please enter the bot token in '/data/config.yaml' | bot -> token")
        exit(2)
    logging.debug("Awaiting bot...")
    await bot.start(token)


if __name__ == "__main__":
    print("Starting Proud Circle Bot...")
    asyncio.run(main())
