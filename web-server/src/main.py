import os.path
import sqlite3

import requests
import humanize as humanize

from util.mcuuid import MCUUID

from flask import Flask, render_template, request

app = Flask(__name__)

# Register the intcomma filter
app.jinja_env.filters['intcomma'] = humanize.intcomma


def connect_db():
	path = os.path.abspath("../../discord-bot/src/data/proudcircle.db")
	conn = sqlite3.connect(path)
	return conn


def get_uuid_from_entry(entry):
	if len(entry) > 17:
		return entry

	r = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{entry}")
	data = r.json()
	uuid = data.get("id", None)
	return uuid


def get_name_from_entry(entry):
	if len(entry) < 17:
		return entry

	r = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{entry}")
	data = r.json()
	name = data.get("name", None)
	return name


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/query_database', methods=['POST'])
def query_database():
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	player = MCUUID(name=request.form['player_name'])
	uuid = player.uuid
	player_name = player.name
	conn = connect_db()
	c = conn.cursor()
	c.execute("SELECT * FROM expHistory WHERE date BETWEEN ? AND ? AND uuid = ? ORDER BY date ASC",
	          (start_date, end_date, uuid))
	results = c.fetchall()
	conn.close()
	data = {
		"playername": player_name,
		"expHistory": results
	}
	return render_template('results.html', data=data)


if __name__ == "__main__":
	app.run()



