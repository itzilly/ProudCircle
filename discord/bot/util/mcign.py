import requests
from util.uuid_database import UuidDb


class MCIGN:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.uuid = None
        self.hyphenated_uuid = None
        self.name_history = None

        located = False
        for entry in UuidDb.database:
            for key, value in entry.items():
                if value == self.id:
                    located = True
                    self.uuid = entry['uuid']
                    self.name = entry['name']

        if not located:
            uri = "https://playerdb.co/api/player/minecraft/" + self.id
            response = requests.get(uri).json()
            data = response['data']['player']
            target_entry = {'uuid': data['raw_id'], 'name': data['username']}
            UuidDb.add_entry(target_entry)
            self.name = target_entry['name']
            self.uuid = target_entry['uuid']
