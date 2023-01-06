import os
import json
import sqlite3
import requests

from datetime import datetime


CONFIG_PATH = "./config.json"
DATABASE_PATH = "./expHistory.db"


def check_table_structure(sqlite_cur):
	sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expHistory';")
	if not sqlite_cur.fetchone():
		# Table does not exist, create it
		sqlite_cur.execute('''CREATE TABLE expHistory
					 (timestamp text, date text, uuid text, amount int, rank text)''')
	else:
		# Table exists, check that it has the correct columns
		sqlite_cur.execute("PRAGMA table_info(expHistory);")
		column_info = sqlite_cur.fetchall()
		column_names = [column[1] for column in column_info]
		if "timestamp" not in column_names:
			sqlite_cur.execute("ALTER TABLE expHistory ADD COLUMN timestamp text;")
		if "date" not in column_names:
			sqlite_cur.execute("ALTER TABLE expHistory ADD COLUMN date text;")
		if "uuid" not in column_names:
			sqlite_cur.execute("ALTER TABLE expHistory ADD COLUMN uuid text;")
		if "amount" not in column_names:
			sqlite_cur.execute("ALTER TABLE expHistory ADD COLUMN amount int;")
		if "rank" not in column_names:
			sqlite_cur.execute("ALTER TABLE expHistory ADD COLUMN rank text;")
	sqlite_cur.connection.commit()


def sync_exp_history(member, sqlite_cur):
	uuid = member["uuid"]
	rank = member["rank"]
	xp_history = member["expHistory"]
	print(f"Syncing Member: {member['uuid']}")

	for date, amount in xp_history.items():
		if str(date).startswith("2022"):
			print(f"Skipping date: {date}")
			continue

		sqlite_cur.execute("SELECT * FROM expHistory WHERE uuid=? AND date=?", (uuid, date))
		result = sqlite_cur.fetchone()
		if result:
			recorded_amount = result[3]
			if recorded_amount != amount:
				print(f"Updating unsynced data: {result} | {amount} {uuid} {date}")
				sqlite_cur.execute("UPDATE expHistory SET timestamp=?, amount=? WHERE uuid=? AND date=?", (
					datetime.now().timestamp(), amount, uuid, date))
		else:
			print(f"Syncing dataL {date} {uuid} {amount} {rank}")
			sqlite_cur.execute("INSERT INTO expHistory (timestamp, date, uuid, amount, rank) VALUES (?, ?, ?, ?, ?)", (
				datetime.now().timestamp(), date, uuid, amount, rank))
	sqlite_cur.connection.commit()


def main() -> None:
	if not os.path.exists(CONFIG_PATH):
		config_data = {"guild_id": None, "key": None}
		with open(CONFIG_PATH, 'w') as config_file:
			json.dump(config_data, config_file)

	with open(CONFIG_PATH, 'r') as config_file:
		config = json.load(config_file)

	sqlite_database = sqlite3.connect(DATABASE_PATH)
	cursor = sqlite_database.cursor()
	check_table_structure(cursor)

	guild_id = config["guild_id"]
	key = config["key"]
	url = f"https://api.hypixel.net/guild?key={key}&id={guild_id}"
	data = requests.get(url)
	# ratelimit_remaining = data.headers["RateLimit-Remaining"]
	guild_data = data.json()
	if not guild_data["success"]:
		print(f"Unsuccessful in scraping api data: {data.headers} | {guild_data}")
		return

	guild_members = guild_data.get("guild", {}).get("members", {})
	for member in guild_members:
		sync_exp_history(member, cursor)


if __name__ == "__main__":
	main()
