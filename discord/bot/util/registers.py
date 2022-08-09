# TODO: Rename all tasks to better names
# TODO: Add main settings/config in this file
import os
import yaml
import time
import logging

import util.uuid_database


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
    registries = [GuildRegistry]
    for register in registries:
        try:
            register.load()
        except Exception as e:
            logging.critical(f"Error loading register {register.__name__}: {e}")
    if not os.path.exists(util.uuid_database.UuidDb._path):
        util.uuid_database.UuidDb.generate()
    util.uuid_database.UuidDb.load()
