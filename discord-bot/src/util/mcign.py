import logging
import re

import requests


class MCIGN:
	def __init__(self, player_id=None):
		assert (player_id is not None)
		self._id = player_id
		self._name = None
		self._uuid = None

	@property
	def uuid(self):
		if self._uuid is None:
			self._load()
		return self._uuid

	@property
	def name(self):
		if self._name is None:
			self._load()
		return self._name

	def _load(self):
		if len(self._id) < 17:
			url = f"https://api.mojang.com/users/profiles/minecraft/{self._id}"
		else:
			url = f"https://sessionserver.mojang.com/session/minecraft/profile/{self._id}"
		r = requests.get(url)
		data = r.json()
		self._name = data.get("name", None)
		self._uuid = cleanup_uuid(data.get("id", None))


def is_valid_minecraft_username(username):
	"""https://help.mojang.com/customer/portal/articles/928638-minecraft-usernames"""
	allowed_chars = 'abcdefghijklmnopqrstuvwxyz1234567890_'
	allowed_len = [2, 16]

	username = username.lower()

	if len(username) < allowed_len[0] or len(username) > allowed_len[1]:
		return False

	for char in username:
		if char not in allowed_chars:
			return False

	return True


def is_valid_mojang_uuid(uuid):
	"""https://minecraft-de.gamepedia.com/UUID"""
	allowed_chars = '0123456789abcdef'
	allowed_len = 32

	uuid = uuid.lower()
	uuid = cleanup_uuid(uuid)

	if len(uuid) != allowed_len:
		return False

	for char in uuid:
		if char not in allowed_chars:
			return False

	return True


def cleanup_uuid(uuid):
	uuid = uuid.replace('-', '')
	return uuid


def dash_uuid(uuid):
	if len(uuid) == 36:
		return uuid
	dashed_uuid = re.sub(r"([0-9a-f]{8})([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]+)", r"\1-\2-\3-\4-\5", uuid)
	return dashed_uuid
