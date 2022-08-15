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
                    'config_version': '1.1.2',
                    'bot_version': 'Pre-v1.0.0'
                },
                'bot': {
                    'token': None
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
                        'verification': None,
                        'welcome': None,
                        'leave': None,
                        'rules': None,
                        'bot_commands': None
                    },
                    'message_ids': {
                        'verification_id': None
                    }
                },
                'hypixel': {
                    'guid_id': "6177d2d68ea8c9a202fc277a",
                    'api_key': None
                },
                'setup': {
                    'has_rules': False,
                    'has_verification': False,
                    # 'has_'
                }
            }

    @staticmethod
    def reload():
        """
        Loads configuration data
        """
        logging.debug("Reloading main configuration file")
        with open(Settings._config_path) as file:
            _data = yaml.safe_load(file)
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
        Settings.reload()

    @staticmethod
    def load_configuration():
        """Loads the configuration file into memory for the first time"""
        # Generate file if it does not exist
        if not os.path.exists(Settings._config_path):
            logging.info("Generating main configuration file")
            with open(Settings._config_path, 'w') as file:
                yaml.dump(Settings.get_settings_build(), file)

        # Load config file into memory
        logging.debug("Loading main configuration file")
        with open(Settings._config_path) as file:
            _data = yaml.safe_load(file)
        Settings.config = _data

        if _data.get('hypixel').get('api_key') is None:
            logging.critical("No Hypixel API key detected! Most features will be disabled! Run `/setapikey "
                             "<YourApiKey>`")
