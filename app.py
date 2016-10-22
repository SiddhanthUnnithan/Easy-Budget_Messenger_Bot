import os
import sys
import json

import requests
from flask import Flask, jsonify, request

from pymongo import MongoClient
import psycopg2

app = Flask(__name__)

ec2_ip = '54.224.111.118'

# mongo client instantiation
client = MongoClient(ec2_ip, 27017)
db = client.budget

# HELPERS
def log(message):
	print(str(message))
	sys.stdout.flush()


def send_message(recipient_id, message_data):
	log("sending message to %s" % (recipient_id))

	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}

	headers = {
		"Content-Type": "application/json"
	}

	data = json.dumps({
		"recipient": {
            "id": recipient_id
        },
        "message": message_data
	})

	r = requests.post("https://graph.facebook.com/v2.6/me/messages",
					  params=params, headers=headers, data=data)

	if r.status_code != 200:
		log(r.status_code)
		log(r.text)


def postgrescmd():
	conn = psycopg2.connect(user="mcga", password="Welcome1", host=ec2_ip)
	crs = conn.cursor()

	# test table creation
	crs.execute("""
		CREATE TABLE test (
			author VARCHAR(50),
			message VARCHAR(100)
		);
	""")

	# test table insertion
	crs.execute("""
		INSERT INTO test (author, message)
			VALUES ('mcga', 'hello world')
	""")

	# test table querying
	crs.execute("""
		SELECT author, message FROM test;
	""")

	cols = [desc[0] for desc in crs.description]

	res = crs.fetchone()

	return dict(zip(cols, res))


def mongocmd():
	client = MongoClient(ec2_ip, 27017)
	db = client.test
	coll = db.coll

	# test an insertion
	test_post = {'author': 'mcga', 'text': 'hello_world'}
	uid = coll.insert_one(test_post).inserted_id

	# test a retrieval
	res = coll.find_one({"_id":uid})

	if res is None:
		return "Empty result set."

	return res


@app.route("/", methods=['GET'])
def verify():
	"""
		when endpoint is registered as webhook, it must echo back
		'hub.chalenge' value it receives in query arguments
	"""
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200

	return "Hello world", 200


@app.route("/", methods=["POST"])
def webhook():
	# process incoming messaging events

	data = request.get_json()
	log(data)

	trxn_coll = db.trxn

	message_data = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
                    "title": "Add Income",
                    "subtitle": "Add Instantaneous Income",
                    "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Set Income Amount",
	                        "payload": "Payload for first element in a generic bubble"
	                    }
                    ],
                }, {
                    "title": "Expenditure",
                    "subtitle": "Add Instantaneous Expenditure",
                    "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Set Expenditure Amount",
	                        "payload": "Payload for second element in a generic bubble"
	                    }
                    ],
                },
                {
                	"title": "Set A Goal",
                	"subtitle": "Goal Setting Card.",
                	"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                	"buttons": [
                		{
                			"type": "postback",
                			"title": "Add Goal",
                			"payload": "Payload for first button in third element"
                		},
                		{
                			"type": "postback",
                			"title": "Review Goals",
                			"payload": "Payload for second button in third element"
                		}
                	]
                }]
			}
		}
	}

	onboarding_data = {
		"setting_type": "greeting",
		"greeting": {
			"text": "Hi {{user_first_name}}, welcome to ProsperCA's Easy Budget Bot."
		}
	}

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				print messaging_event["sender"]
				sender_id = messaging_event["sender"]["id"]
				recipient_id = messaging_event["recipient"]["id"]

				if messaging_event.get("message"):
					# arbitrary message has been received
					message_text = messaging_event["message"]["text"]

					# check to see if user exists in database
					res = trxn.find_one({"user_id": sender_id})

					if res is None:
						# onboard user
						send_message(sender_id, onboarding_data)
						continue

					if message_text == "Options":
						send_message(sender_id, message_data)
						continue
					
					send_message(sender_id, {"text": "messaged received, thanks!"})

				if messaging_event.get("delivery"):
					# confirm delivery
					pass

				if messaging_event.get("optin"):
					# optin confirmation
					pass

				if messaging_event.get("postback"):
					# user clicked/tapped "postback" button in earlier message
					pass

	return "ok", 200


@app.route("/mongotest")
def mongo():
	# res = mongocmd()
	# return jsonify(author=res['author'], text=res['text'])
	return "mongotest -- placeholder"

@app.route("/pgtest")
def postgres():
	# res = postgrescmd()
	# return jsonify(author=res['author'], message=res['message'])
	return "pgtest -- placeholder"


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
