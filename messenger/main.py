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
			payload = request.getData()
			for message, sender in message_events(payload):
				print("Incoming post from %s, %s" %(sender,message))
				send_message(sender, message)
			return "okay"
			#text = data['entry'][0]['messaging'][0]['message']['text']
			#sender = data['entry'][0]['messaging'][0]['sender']['id']
			#payload = {'recipient': {'id': sender}, 'message': {'text': "Hello World"}}
			
		except Exception as e:
			print("Something went wrong")

	elif request.method == 'GET':
		if request.args.get('hub.verify_token') == config.env['verify_token']:
			return request.args.get('hub.challenge')
		return "Wrong Verify Token"

	return "Hello World"

#function to generate a list of [id, messageText] from payload
def messaging_events(payload):
	data = json.loads(request.data)
	messaging_events = data["entry"][0]["messaging"]
	
	for event in messaging_events:
		if "message" in event and "text" in event["message"]:
			yield event ["sender"]["id"], "test"
			
			
#send the message 'text' to 'recipient'			
def send_message (recipient, text):
	
	global token
	r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, data=json.dumps({
	"reciepient": {"id": recipient},
	"message":{"text":
	           text.decode('unicode_escape')}
	           }),
			  headers={'Content-type':'application/json'})
	if r.status_code != requests.codes.ok:
		print(r.text)
