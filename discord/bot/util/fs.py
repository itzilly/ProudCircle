import os
import logging

from util import uuid_database
from util import config_handler
from util import linked_database


def get_all_extensions():
    ext = []
    for file in os.listdir('./extensions'):
        if file.endswith('.py'):
            ext.append(f"extensions.{file.replace('.py', '')}")
    logging.debug(f"Found {len(ext)} extension(s): {[f for f in ext]}")
    return ext


def load_files():
    config_handler.Settings.load_configuration()
    uuid_database.UuidDb.load_database()
    linked_database.LinkedDatabase.load_database()
