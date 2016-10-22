import os
import sys
import json

import requests
from flask import Flask, jsonify, request

from pymongo import MongoClient
import psycopg2

app = Flask(__name__)

ec2_ip = '52.205.251.79'

# mongo client instantiation
client = MongoClient(ec2_ip, 27017)
db = client.budget
# relevant collections
user_coll = db.users
trxn_coll = db.trxn
state_coll = db.state
goal_coll = db.goals

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

	# retrieve state map from mongo
	state_obj = state_coll.find_one()

	state_id = state_obj["_id"]

	state_map = state_obj["map"]

	print state_id

	print state_map

	data = request.get_json()
	log(data)

	main_quick_reply = {
		"text": "Would you like to see your balance",
		"quick_replies": [
			{
				"content_type": "text",
				"title": "Yes",
				"payload": "SEE_BALANCE_YES"
			},
			{
				"content_type": "text",
				"title": "No",
				"payload": "SEE_BALANCE_NO"
			}
		]
	}

	main_balance = {
		"text": "Your balance is over $9000!!!"
	}

	main_carousel = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
                    "title": "Add Income",
                    "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Set Income Amount",
	                        "payload": "SET_INCOME"
	                    }
                    ],
                }, {
                    "title": "Add Expenses",
                    "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Set Expenses Amount",
	                        "payload": "SET_EXPENSES"
	                    }
                    ],
                },
                {
                	"title": "Visualization",
                	"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                	"buttons": [
                		{
                			"type": "postback",
                			"title": "Visualize Your Goal",
                			"payload": "GOAL_VISUALIZATION"
                		}
                	]
                }]
			}
		}
	}

	onboarding_greeting = {
		"text": "Hey! Prosper Canada wants to make budgeting personal :). I'm here to help you set and achieve your financial goals by making it easy for you to track your income and expenses!"
	}

	onboarding_goal_title = {
		"text": "Let's get started by creating a goal for you. What would you like to name your goal?"
	}

	onboarding_goal_desc = {
		"text": "Great, please add a small description for your goal."
	}

	onboarding_goal_amount = {
		"text": "Awesome! What would you like your goal amount to be?"
	}

	onboarding_curr_balance = {
		"text": "Great, for final touches I'm going to need you to enter your current balance."
	}

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				print messaging_event["sender"]
				sender_id = messaging_event["sender"]["id"]
				recipient_id = messaging_event["recipient"]["id"]

				if messaging_event.get("postback"):
					# user clicked/tapped "postback" button in earlier message
					message_payload = messaging_event["postback"]["payload"]

					if message_payload == "SET_INCOME":
						pass
					if message_payload == "SET_EXPENSES":
						pass
					if message_payload == "GOAL_VISUALIZATION":
						pass

				if messaging_event.get("message"):
					# arbitrary message has been received
					message_text = messaging_event["message"]["text"]

					# check to see if user exists in database
					res = user_coll.find_one({"user_id": int(sender_id)})

					if res is None:
						# insert user in collection
						user_coll.insert({
							"user_id": sender_id,
							"is_onboarded": False,
							"current_balance": None
						})

					if res is None or res["is_onboarded"] == False:
						# create goal record in mongo database
						goal_coll.insert(
							{"user_id": sender_id, "goal_title": None,
							 "goal_desc": None, "goal_amount": None,
							 "is_achieved": False})

						# onboard user
						if not state_map["goal_title"]["is_message_sent"]:
							send_message(sender_id, onboarding_greeting)
							send_message(sender_id, onboarding_goal_title)
							state_coll.update({"_id": state_id}, {
								"$set": {
									"map.goal_title.is_message_sent": True
								}
							}, upsert=False)
							continue
						elif goal_coll.find_one({"user_id": sender_id})["goal_title"] is None:
							goal_coll.update({"user_id": sender_id}, {
								"$set": {
									"goal_title" : message_text 
								}
							}, upsert=False)

						if not state_map["goal_desc"]["is_message_sent"]:
							send_message(sender_id, onboarding_goal_desc)
							state_coll.update({"_id": state_id}, {
								"$set": {
									"map.goal_desc.is_message_sent": True
								}
							}, upsert=False)
							continue

						elif goal_coll.find_one({"user_id": sender_id})["goal_desc"] is None:
							goal_coll.update({"user_id": sender_id}, {
								"$set": {
									"goal_desc" : message_text 
								}
							}, upsert=False)	


						if not state_map["goal_amount"]["is_message_sent"]:
							send_message(sender_id, onboarding_goal_amount)
							state_coll.update({"_id": state_id}, {
								"$set": {
									"map.goal_amount.is_message_sent": True
								}
							}, upsert=False)
							continue
						elif goal_coll.find_one({"user_id": sender_id})["goal_amount"] is None:
							goal_coll.update({"user_id": sender_id}, {
								"$set": {
									"goal_amount" : float(message_text) 
								}
							}, upsert=False)
							# future work: ask for confirmation

						if not state_map["curr_balance"]["is_message_sent"]:
							send_message(sender_id, onboarding_curr_balance)
							state_coll.update({"_id": state_id}, {
								"$set": {
									"map.curr_balance.is_message_sent": True
								}
							}, upsert=False)
							continue
						elif user_coll.find_one({"user_id": sender_id})["current_balance"] is None:
							user_coll.update({"user_id": sender_id}, {
								"$set": {
									"current_balance" : float(message_text) 
								}
							}, upsert=False)

							user_goal = goal_coll.find_one({"user_id": sender_id})

							summary = "Here's a summary of your goals: Goal Title: %s, Goal Desc: %s, Goal Amount: %s."  \
								% (user_goal["goal_title"], user_goal["goal_desc"], user_goal["goal_amount"],
								   user_coll.find_one({"user_id": sender_id})["current_balance"])

							# update the user record to complete onboarding
							user_coll.update({"user_id": sender_id}, {
								"$set": {
									"is_onboarded" : True 
								}
							}, upsert=False)

							send_message(sender_id, {"text": summary})
							send_message(sender_id, main_quick_reply)

						continue

					# income

					# expenses

					if messaging_event["message"].get("quick_reply"):
						message_payload = messaging_event["message"]["quick_reply"]["payload"]

						if message_payload == "SEE_BALANCE_YES":
							send_message(sender_id, main_balance)
							send_message(sender_id, main_carousel)
							continue
						if message_payload == "SEE_BALANCE_NO":
							send_message(sender_id, {"text": "Then have a nice day."})
							continue
						continue

					if message_text == "Main Menu":
						send_message(sender_id, main_balance)
						send_message(sender_id, main_carousel)
						continue

					send_message(sender_id, main_quick_reply)

				if messaging_event.get("delivery"):
					# confirm delivery
					pass

				if messaging_event.get("optin"):
					# optin confirmation
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
