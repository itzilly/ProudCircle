import os
import yaml
import logging


class Settings:
    config = None
    _config_path = './data/config.yaml'
    _data = None

    @staticmethod
    def get_settings_build():
        return {
                'info': {
                    'config_version': '1.0.0',
                    'bot_version': 'Pre-v1.0.0'
                },
                'bot': {
                    'token': "No Token"
                },
                'discord': {
                    'server_id': None,
                    'has_been_setup': False,
                    'roles_have_been_created': False,
                    'role_ids': {
                        'bot_admin': None,
                        'discord_staff': None,
                        'guild_staff': None,
                        'guild_champion': None,
                        'guild_celestial': None,
                        'guild_legend': None,
                        'guild_member': None,
                        'discord_guest': None,
                        'verified': None,
                        'everyone': None
                    },
                    'channel_ids': {
                        'verification': 0,
                        'welcome': 0,
                        'leave': 0,
                        'rules': 0
                    }
                },
                'hypixel': {
                    'guid_id': 0,
                    'api_key': 0
                }
            }

    @staticmethod
    def _load_file():
        """
        Reads config file stream into python object.
        """
        with open(Settings._config_path) as file:
            data = yaml.safe_load(file)
        return data

    @staticmethod
    def _generate_file():
        """
        Generates default main configuration file.
        """
        with open(Settings._config_path, 'w') as file:
            yaml.dump(Settings.get_settings_build(), file)
        logging.info("Generated main configuration file")

    @staticmethod
    def first_load():
        """
        Loads the main configuration for the first time upon run.
        This should be called on startup every time only once in the
        program's life.
        """
        if Settings.config is not None:
            return logging.warning("Attempted to first load configuration file again!")
        if not os.path.exists(Settings._config_path):
            logging.warning("No configuration file found! NOTE: If this is the first time you're running the bot you can ignore this message.")
            Settings._generate_file()

        settings = Settings._load_file()
        test = settings['bot']['token']

        if test is None:
            logging.critical("No bot token detected! Please enter your bot token in '/data/config.yaml' | bot -> token")
            exit(2)
        if len(test) > 10:
            logging.critical("No bot token detected! Please enter your bot token in '/data/config.yaml' | bot -> token")
            exit(2)

    @staticmethod
    def load():
        """
        Loads configuration data
        """
        logging.debug("Loading main configuration file")
        _data = Settings._load_file()
        Settings.config = _data

    @staticmethod
    def update_config(new_config_data):
        """
        Updates configuration file with new object
        """
        logging.debug("Updating configuration file")
        with open(Settings._config_path, 'w') as file:
            yaml.dump(new_config_data, file)
        logging.debug("Configuration file updated")
        Settings.config = Settings._load_file()
