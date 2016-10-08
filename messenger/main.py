from flask import *
import config
import json
import traceback
import random
import requests

token = config.env['access_token']


main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def main_route():
	if request.method == 'POST':
		try:
			data = json.loads(request.data)
			text = data['entry'][0]['messaging'][0]['message']['text']
			sender = data['entry'][0]['messaging'][0]['sender']['id']
			payload = {'recipient': {'id': sender}, 'message': {'text': "Hello World"}}
			r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, json=payload)
		except Exception as e:
			print("Something went wrong")

	elif request.method == 'GET':
		if request.args.get('hub.verify_token') == config.env['verify_token']:
			return request.args.get('hub.challenge')
		return "Wrong Verify Token"

	return "Hello World"
