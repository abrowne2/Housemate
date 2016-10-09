from flask import *
import sys
sys.path.insert(0, '.')
import config
import json
import traceback
import random
import requests
from model import Conversation
from pymongo import MongoClient

token = config.env['access_token']

#add in the mongo server in the instance call
client = MongoClient('mongodb://localhost:27017/')
convos = client.conversations


responses = ["Did you mean:\n",  # Convo state 0
			"Are you looking for an appartment, house or both?\n", # Convo state 1
			"How many bedrooms?\n", # Convo state 2
			"What's your price range?\n" # Convo state 4
			]
			

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def main_route():
	if request.method == 'POST':
		try:
			payload = request.get_json()
			for message, sender in messaging_events(payload):
				# if a convo with this sender exists, run the appropriate protocol

				found = convos.find_one({"id": sender}).count()
				
				if  found != 0:
					temp = Conversation(sender);
					temp.prefs = found["prefs"]
					temp.curState = found["curState"]
					temp.id = found["id"]
					temp.numBeds = found["numBeds"]
					parse_and_respond(temp, message)
					#convos.update_one({"id": sender}, temp)
				else:
					temp = Conversation(sender);
					convos.insert_one(temp)
					message = "Initial question  as result of function here"

			return "okay"
			
		except Exception as e:
			print(type(e))
			print(e.args)

	elif request.method == 'GET':
		if request.args.get('hub.verify_token') == config.env['verify_token']:
			return request.args.get('hub.challenge')
		return "Wrong Verify Token"

	return "Hello World"

#function to generate a list of [id, messageText] from payload
def messaging_events(payload):
	data = payload
	messaging_events = data["entry"][0]["messaging"]
	
	for event in messaging_events:
		if "message" in event and "text" in event["message"]:
			yield event["message"]["text"], event["sender"]["id"]
			
			
#send the message 'text' to 'recipient'			
def send_message (recipient, text):
	r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, data=json.dumps({
		"recipient": {"id": recipient},
		"message": {"text": text}
	}),
	headers={'content-type':'application/json'})
	if r.status_code != requests.codes.ok:
		print(r.text)

def send_results (recipient, reults):
	res = {
		"recipient": {"id": recipient},
		"message": {
			"attachment": {
				"type": "template",
				"payload": {
					"template_type": "generic",
					"elements": []
				}
			}
		}
	}
	for result in results:
		res["message"]["attachment"]["payload"]["elements"].append({
			"title": result["name"],
			"item_url": result["url_path"],
			"image_url": result["image_url"],
			"subtitle": result["address"] + ", " + result["city"],
			"buttons": [
				{
					"type": "web_url",
					"url": result["url_path"],
					"title": "View Listing"
				}
			]
		})
	r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token, data=json.dumps(res),
		headers={'content-type':'application/json'})
	if r.status_code != requests.codes.ok:
		print(r.text)

# Determine the relevant function to parse user input and respond with the next relevant question
def parse_and_respond(convo, message):
	convo_state = convo.curState
	if convo_state == 0:
		try:
			convo.ACParser(message)
			send_message(convo.id, responses[0] + convo.acResultsToString())
			convo.incrState()
		except Exception as e:
			send_message(convo.id, "I'm sorry, I didn't quite get that, can you rephrase?")
			convo.curState = 0

	elif convo_state == 1:
		try:
			convo.acIndexParse(message)
			send_message(convo.id, responses[1])
			convo.incrState()
		except Exception as e:
			send_message(convo.id, "I'm sorry, I didn't quite get that, can you rephrase?")
			convo.curState = 1

	elif convo_state == 2:
		try:
			convo.optionPrs(message)
			send_message(convo.id, responses[2])
			convo.incrState()
		except Exception as e:
			send_message(convo.id, "I'm sorry, I didn't quite get that, can you rephrase?")
			convo.curState = 2

	elif convo_state == 3:
		try:
			convo.bedBathPrs(message)
			send_message(convo.id, responses[3])
			convo.incrState()
		except Exception as e:
			send_message(convo.id, "I'm sorry, I didn't quite get that, can you rephrase?")
			convo.curState = 3

	elif convo_state == 4:
		try:
			convo.pricePrs(message)
			results = convo.preferentialSearch()
			send_results(convo.id, results)
			convo.curState = 0
			send_message(convo.id, "Where else would you like to look for housing?")
		except Exception as e:
			send_message(convo.id, "I'm sorry, I don't understand, can you rephrase?")
			convo.curState = 4

	else:
		convo.curState = 0

	return


