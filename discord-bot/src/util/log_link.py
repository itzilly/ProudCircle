import json
import logging

import discord
import requests

bot = None
logging_channel = None


def debug_message(message):
	pass


def debug_embed(embed: discord.Embed):
	pass


def info_message(message):
	pass


def info_embed(embed: discord.Embed):
	pass


def task_webhook(embed):
	url = "https://discord.com/api/webhooks/1066657524629110865/" \
		"QCan3w-d7rkQXEM2xNf4oyohHogrWLBwLZr4cpdao46O1Bhj5ly5ksvZMp7Y11Oogg3J"

	data = {"embeds": [embed]}
	headers = {'Content-Type': 'application/json'}

	response = requests.post(url, data=json.dumps(data), headers=headers)

	try:
		response.raise_for_status()
	except requests.exceptions.HTTPError as err:
		logging.error(err)
