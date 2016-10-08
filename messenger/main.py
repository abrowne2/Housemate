from flask import *
import config
import json
import traceback
import random
import requests
from model import Conversation
from pymongo import MongoClient

token = config.env['access_token']

#add in the mongo server in the instance call
client = MongoClient()
convos = client.conversations

responses = ["What university do you attend?", # Convo state 0
				"Did you mean:",  # Convo state 1
				"Are you looking for an apartment, house or both?", # Convo state 2
				"How many bedrooms?", # Convo state 3
				"What's your price range?", # Convo state 4
				"Are you concerned about crime in your neighborhood?"] # Convo state 5

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def main_route():
	if request.method == 'POST':
		try:
			payload = request.getData()
			for message, sender in message_events(payload):
				# if a convo with this sender exists, run the appropriate protocol
				found = convos.find_one({"id": sender})
				if  found != "":
					temp = Conversation();
					temp.prefs = found["prefs"]
					temp.curState = found["curState"]
					temp.id = found["id"]
					temp.numBeds = found["numBeds"]
					
					parse_and_respond(temp, message)
					convos.update_one({"id": sender}, temp)
				else:
					# need to change
					#convos.insert_one(temp)
					message = "Initial question  as result of function here"


			return "okay"
			
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

# Determine the relevant function to parse user input and respond with the next relevant question
def parse_and_respond(convo, message):
	convo_state = convo.curState
	if convo_state == 0:
		send_message(convo.id, responses[0])

	elif convo_state == 1:
		parse_for_autocomplete(message, convo)
		send_message(convo.id, responses[1] + enumerate(convo.acresults))

	elif convo_state == 2:
		parse_for_type(message, convo)
		send_message(convo.id, responses[2])

	elif convo_state == 3:
		parse_for_bedrooms(message, convo)
		send_message(convo.id, responses[3])

	elif convo_state == 4:
		parse_for_price(message, convo)
		send_message(convo.id, responses[5])

	elif convo_state == 5:
		parse_for_crime(message, convo)
		# return final results here

	convo.incrState()


