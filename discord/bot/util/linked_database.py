import os
import json
import logging


class LinkedDatabase:
    database = None
    _path = './data/registers/linked.json'

    @staticmethod
    def generate():
        if not os.path.exists(LinkedDatabase._path):
            logging.debug("Generating Linked Database")
            with open(LinkedDatabase._path, 'w') as file:
                file.write("[]")
        return True

    @staticmethod
    def load():
        logging.debug("Loading Linked Database")
        with open(LinkedDatabase._path) as file:
            _data = json.load(file)
        LinkedDatabase.database = _data

    @staticmethod
    def add_entry(entry: dict):
        LinkedDatabase.database.append(entry)
        with open(LinkedDatabase._path, 'w') as file:
            json.dump(LinkedDatabase.database, file, indent=4)
        LinkedDatabase.load()

    @staticmethod
    def add_entries(entries: list):
        LinkedDatabase.database.extend(entries)
        with open(LinkedDatabase._path, 'w') as file:
            json.dump(LinkedDatabase.database, file, indent=4)
        LinkedDatabase.load()
