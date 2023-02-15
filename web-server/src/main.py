import sqlite3
import requests

from flask import Flask, render_template, request


app = Flask(__name__)


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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_name = request.form['player_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        conn = connect_db()
        c = conn.cursor()
        query = f"SELECT * FROM expHistory WHERE player_name='{player_name}'"
        c.execute(query)
        results = c.fetchall()
        return render_template('results.html', results=results)
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
