import os
import json
import logging


class UuidDb:
    database = None
    _path = './data/registers/uuids.json'

    @staticmethod
    def generate():
        if not os.path.exists(UuidDb._path):
            logging.debug("Generating uuid db")
            with open(UuidDb._path, 'w') as file:
                file.write("[]")
        return True

    @staticmethod
    def load():
        logging.debug("Loading uuid db")
        with open(UuidDb._path) as file:
            _data = json.load(file)
        UuidDb.database = _data

    @staticmethod
    def add_entry(entry: dict):
        UuidDb.database.append(entry)
        with open(UuidDb._path, 'w') as file:
            json.dump(UuidDb.database, file, indent=4)
        UuidDb.load()

    @staticmethod
    def add_entries(entries: list):
        UuidDb.database.extend(entries)
        with open(UuidDb._path, 'w') as file:
            json.dump(UuidDb.database, file, indent=4)
        UuidDb.load()
