import sqlite3

import humanize as humanize
import requests

from flask import Flask, render_template, request


app = Flask(__name__)

# Register the intcomma filter
app.jinja_env.filters['intcomma'] = humanize.intcomma


def connect_db():
    conn = sqlite3.connect(r"O:\Python Programming\ProudCircle\discord-bot\src\data\proudcircle.db")
    return conn


def get_uuid_from_entry(entry):
    if len(entry) > 17:
        return entry

    r = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{entry}")
    data = r.json()
    uuid = data.get("id", None)
    return uuid


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query_database', methods=['POST'])
def query_database():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    player_name = get_uuid_from_entry(request.form['player_name'])
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM expHistory WHERE date BETWEEN ? AND ? AND uuid = ? ORDER BY date ASC",
              (start_date, end_date, player_name))
    results = c.fetchall()
    conn.close()
    data = {"playername": player_name}
    return render_template('results.html', results=results, data=data)


if __name__ == "__main__":
    app.run()
