# TODO: Rename all tasks to better names
# TODO: Add main settings/config in this file
import os
import yaml
import time
import logging


def get_uuid_registry_build():
    # The default, empty build of the
    # uuids registry dictionary
    uuid_registry_build = {
        'info': {
        'time_generated': time.time(),
        'last_updated': None
        },
        'uuids': []
    }
    return uuid_registry_build

def get_guild_registry_build():
    guild_registry_build = {
        'info': {
            'time_generated': time.time(),
            'last_updated': None,
        },
        'guild': {
            'members': [],
            'ranks': []
        }
    }


class UuidRegistry:
    data = None
    _uuid_registry_path = "./data/registers/uuids.registry"

    @classmethod
    def _load(cls):
        with open(UuidRegistry._uuid_registry_path, 'r') as uuid_reg_file:
            _uuid_registry = yaml.load(uuid_reg_file, Loader=yaml.SafeLoader)
        return _uuid_registry

    @classmethod
    def _generate(cls):
        if os.path.exists(UuidRegistry._uuid_registry_path):
            return True
        logging.warning("No uuid registry file detected")
        logging.debug("Generating uuids registry...")
        with open(UuidRegistry._uuid_registry_path, 'w') as uuid_reg_file:
            write_task = yaml.dump(
                get_uuid_registry_build(),
                uuid_reg_file,
                sort_keys=True,
                indent=2    
            )
        logging.info("Generated uuids registry")
        return False

    @classmethod
    def load(cls):
        logging.debug("Loading uuids registry")
        # Note: Generating registry will not overwrite existing file
        UuidRegistry._generate()
        UuidRegistry.data = UuidRegistry._load()

    @classmethod
    def reload(cls):
        logging.debug("Reloading uuids registry")
        UuidRegistry.data = UuidRegistry._load()

    @classmethod
    def update(new_data):
        assert(isinstance(new_data, dict))
        logging.debug("Updating uuids registry")
        with open(UuidRegistry._uuid_registry_path, 'w') as uuid_reg_file:
            update_task = yaml.dump(
                new_data,
                uuid_reg_file,
                sort_keys=True,
                indent=2
            )
        UuidRegistry.reload()



class GuildRegistry:
    raw_data = None
    data = None
    _guild_registry_path = "./data/registers/guild.registry"

    @classmethod
    def _load(cls):
        with open(GuildRegistry._guild_registry_path, 'r') as guild_reg_file:
            _guild_registry = yaml.load(guild_reg_file, Loader=yaml.SafeLoader)
        return _guild_registry

    @classmethod
    def _generate(cls):
        # TODO: Generate GuildRegistry
        pass

    @classmethod
    def _set_data(cls):
        raw = GuildRegistry.raw_data
        data = {}
        # TODO: Set data (after designing GuildRegistry build)

    @classmethod
    def load(cls):
        logging.debug("Loading guild registry")
        # Note: Generating registry will not overwrite existing file
        GuildRegistry._generate()

    @classmethod
    def reload(cls):
        logging.debug("Reloading guild registry")
        GuildRegistry._load()
        GuildRegistry.raw_data = GuildRegistry._load()

    @classmethod
    def update(new_data):
        assert(isinstance(new_data, dict))
        logging.debug("Updating guild registry")
        with open(GuildRegistry._guild_registry_path, 'w') as guild_reg_file:
            update_task = yaml.dump(
                new_data,
                guild_reg_file,
                sort_keys=False,
                default_flow_style=False,
                indent=2
            )
        GuildRegistry.reload()


def load_all():
    registries = [UuidRegistry, GuildRegistry]
    for register in registries:
        try:
            register.load()
        except Exception as e:
            logging.critical(f"Error loading register {register.__name__}: {e}")


class Settings:
    config = None
    _config_file_path = './data/config.yaml'

    @classmethod
    def _get_config_build(cls):
        yaml_build = {
            'info': {
                'config_version': '1.0.0',
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
        return yaml_build

    @classmethod
    def load(cls):
        logging.debug("Loading main configuration file")
        with open(Settings._config_file_path) as file:
            _settings = yaml.load(file, Loader=yaml.SafeLoader)
        Settings.config = _settings

    @classmethod
    def reload(cls):
        logging.debug("Reloading main configuration file")
        with open(Settings._config_file_path) as file:
            _settings = yaml.load(file, Loader=yaml.SafeLoader)
        Settings.config = _settings

    @staticmethod
    def update(new_yaml_data):
        logging.debug("Updating main configuration file")
        with open(Settings._config_file_path, 'w') as file:
            new_data = yaml.dump(new_yaml_data, file, sort_keys=False, default_flow_style=False)
        Settings.reload()

    @staticmethod
    def check_token():
        if Settings.config['bot']['token'] is None:
            logging.critical("No bot token detected! Please edit 'bin/data/config.yml' INFO->BOT->TOKEN")

    @staticmethod
    def generate():
        if os.path.exists(Settings._config_file_path):
            Settings.load()
            return True
        logging.warning("No main config file detected")
        logging.debug("Generating main configuration file...")
        with open(Settings._config_file_path, 'w') as config_file:
            task = yaml.dump(
                Settings._get_config_build(),
                config_file,
                sort_keys=False,
                indent=2    
            )
        logging.info("Generated main configuration file")
        Settings.load()
        return False
        
