import os
import json
import logging


class UuidDb:
    database = None
    _path = './data/registers/uuids.json'

    @staticmethod
    def reload():
        logging.debug("Reloading uuid database")
        with open(UuidDb._path) as file:
            _data = json.load(file)
        UuidDb.database = _data

    @staticmethod
    def add_entry(entry: dict):
        UuidDb.database.append(entry)
        with open(UuidDb._path, 'w') as file:
            json.dump(UuidDb.database, file, indent=4)
        UuidDb.reload()

    @staticmethod
    def add_entries(entries: list):
        UuidDb.database.extend(entries)
        with open(UuidDb._path, 'w') as file:
            json.dump(UuidDb.database, file, indent=4)
        UuidDb.reload()

    @staticmethod
    def load_database():
        """Loads uuid database into memory for the first time"""
        # Generate database if it does not exist
        if not os.path.exists(UuidDb._path):
            logging.debug("Generating uuid database")
            with open(UuidDb._path, 'w') as database_file:
                database_file.write("[]")

        # Load database into memory
        logging.debug("Loading uuid database")
        try:
            with open(UuidDb._path, 'r') as database_file:
                UuidDb.database = json.load(database_file)
        except json.JSONDecodeError:
            logging.warning("There was an error parsing the uuid database, regenerating")
            with open(UuidDb._path, 'w') as file:
                file.write("[]")
            UuidDb.database = []
