import os
import json
import logging


class LinkedDatabase:
    database = None
    _path = './data/registers/linked.json'

    @staticmethod
    def reload():
        logging.debug("Reloading linked accounts database")
        with open(LinkedDatabase._path) as file:
            _data = json.load(file)
        LinkedDatabase.database = _data

    @staticmethod
    def add_entry(entry: dict):
        LinkedDatabase.database.append(entry)
        with open(LinkedDatabase._path, 'w') as file:
            json.dump(LinkedDatabase.database, file, indent=4)
        LinkedDatabase.reload()

    @staticmethod
    def add_entries(entries: list):
        LinkedDatabase.database.extend(entries)
        with open(LinkedDatabase._path, 'w') as file:
            json.dump(LinkedDatabase.database, file, indent=4)
        LinkedDatabase.reload()

    @staticmethod
    def load_database():
        """Loads linked database into memory for the first time"""
        # Generate database if it does not exist
        if not os.path.exists(LinkedDatabase._path):
            logging.debug("Generating linked accounts database")
            with open(LinkedDatabase._path, 'w') as database_file:
                database_file.write("[]")

        # Load database into memory
        logging.debug("Loading linked account database")
        try:
            with open(LinkedDatabase._path, 'r') as database_file:
                LinkedDatabase.database = json.load(database_file)
        except json.JSONDecodeError:
            logging.critical("There was an error parsing the linked accounts database")
            exit(2)
