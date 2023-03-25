import logging

from datetime import datetime
from util.local import LOCAL_DATA, UuidCache


class PlayerRetriever:
	def __init__(self, name=None, uuid=None):
		self._name: str = name
		self._uuid: str = uuid
		self._id = name if name is not None else uuid
		self.cache: UuidCache = LOCAL_DATA.cache
		self.TEN_HOURS_TO_SECONDS: int = 43200  # 10 Hours

	async def name(self):
		if self._name is None:
			logging.debug(f"PlayerRetriever: Retrieving player with id: {self._id}")
			cmd = "SELECT id, uuid, name, requestedAt FROM uuidCache WHERE (uuid is ?) OR (name is ?)"
			query = self.cache.cursor.execute(cmd, (self._uuid, self._name))
			result = query.fetchall()
			if len(result) > 1:
				logging.error(f"PlayerRetriever: Duplicate players found, wiping them from the cache")
				self._wipe_player(self._uuid)
				self.request_player_by_uuid(self._uuid)
			elif len(result) == 0:
				self.request_player_by_uuid(self._uuid)
			else:
				cache_entry = result[0]
				if cache_entry is None:
					self.request_player_by_uuid(self._uuid)
				row_id = cache_entry[0]
				uuid = cache_entry[1]
				name = cache_entry[2]
				requested_at = int(cache_entry[3])

				time_now = datetime.now().timestamp()
				formatted_time_now = int(str(time_now).split('.')[0])
				time_delta = datetime.fromtimestamp(requested_at) - datetime.fromtimestamp(formatted_time_now)
				if time_delta.seconds > self.TEN_HOURS_TO_SECONDS:
					logging.debug("PlayerRetriever: Located valid cached player")
					self._uuid = uuid
					self._name = name
				else:
					logging.debug("PlayerRetriever: Removing expired player")
					self._wipe_player(uuid)
					self.request_player_by_uuid(self._uuid)
		return self._name

	async def uuid(self):
		if self._uuid is None:
			self.load_by_name()
		return self._uuid

	def _wipe_player(self, player_id) -> None:
		cmd = "DELETE FROM uuidCache WHERE (uuid = ?) or (name = ?)"
		execution = self.cache.cursor.execute(cmd, (player_id, player_id))
		self.cache.conn.commit()

	def request_player_by_uuid(self, player_uuid):
		pass
