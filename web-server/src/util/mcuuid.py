import json
import requests


class MCUUID:
	def __init__(self, name=None, uuid=None):
		assert not ((name is None and uuid is None) or (name is not None and uuid is not None))
		self._name = name
		self._uuid = uuid

	@property
	def uuid(self):
		self._load_by_name()
		return self._uuid

	@property
	def name(self):
		if self._name is None:
			self._load_by_uuid()
		else:
			self._load_by_name()
		return self._name

	def _load_by_name(self):
		if self._uuid is None:
			r = requests.get("https://api.mojang.com/users/profiles/minecraft/{name}".format(
				name=self._name,
			), headers={
				'Content-Type': 'application/json',
			})
			data = json.loads(r.text)
			self._uuid = data["id"]
			self._name = data["name"]

	def _load_by_uuid(self):
		if self._name is None:
			r = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/{uuid}".format(
				uuid=self._uuid,
			), headers={
				'Content-Type': 'application/json',
			})
			data = json.loads(r.text)
			self._uuid = data["id"]
			self._name = data["name"]