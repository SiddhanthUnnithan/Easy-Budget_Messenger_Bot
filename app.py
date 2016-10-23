import os
import sys
import json
import datetime as dt
import itertools
from content import *

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



	income_amount_prompt = {"text": "How much did you earn today?"}
	income_amount_logged = {"text": "We have logged your income successfully :)"}

	# generate set of sub categories based on dict parsing rules - convenience
	expense_subcategories = []

	# map subcategory payload to subcategory title
	# we store title in the database
	subcategory_map = {}

	subcategory_dicts = [home_expense_categories, living_expense_categories,
						 transportation_expense_categories,
						 personal_expense_categories]

	subcategory_dicts = map(lambda x: x["attachment"]["payload"]["elements"], subcategory_dicts)

	subcategory_dicts = list(itertools.chain.from_iterable(subcategory_dicts))

	for elem in subcategory_dicts:
		expense_subcategories.append(elem["buttons"][0]["payload"])
		subcategory_map[elem["buttons"][0]["payload"]] = elem["title"]

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				sender_id = messaging_event["sender"]["id"]
				recipient_id = messaging_event["recipient"]["id"]

				if messaging_event.get("postback"):
					# user clicked/tapped "postback" button in earlier message
					message_payload = messaging_event["postback"]["payload"]

					if message_payload == "SET_INCOME":
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.income.flow_instantiated": True
							}
						}, upsert=False)

						send_message(sender_id, income_category_carousel)

					elif message_payload == "SET_WAGES_INCOME":
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.income.subcategory": income_map[message_payload]
							}
						}, upsert=False)

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_BENEFITS_INCOME":
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.income.subcategory": income_map[message_payload]
							}
						}, upsert=False)

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_SELF_BUSINESS_INCOME":
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.income.subcategory": income_map[message_payload]
							}
						}, upsert=False)

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_OTHER_INCOME":
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.income.subcategory": income_map[message_payload]
							}
						}, upsert=False)

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_EXPENSES":
						# set state to notify expense flow is instantiated
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.flow_instantiated": True
							}
						}, upsert=False)

						# send all expense subcategories
						send_message(sender_id, expense_categories)

					elif message_payload == "VIEW_GEN_PROGRESS":
						# payload for displaying visualization links
						url = "prosper-canada.herokuapp.com/list?userId=%s" % sender_id

						message = "Please use the following link to navigate to your progress page: %s" % url

						send_message(sender_id, {"text": message})
						send_message(sender_id, main_carousel)

					elif message_payload == "HOME_SUBCATEGORIES":
						# set state to keep track of category chosen
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.category": "housing_expenses"
							}
						}, upsert=False)

						send_message(sender_id, home_expense_categories)

					elif message_payload == "TRANSP_SUBCATEGORIES":
						# set state to keep track of category chosen
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.category": "transportation_expenses"
							}
						}, upsert=False)

						send_message(sender_id, transportation_expense_categories)

					elif message_payload == "LIVING_SUBCATEGORIES":
						# set state to keep track of category chosen
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.category": "living_expenses"
							}
						}, upsert=False)

						send_message(sender_id, living_expense_categories)

					elif message_payload == "PERSONAL_SUBCATEGORIES":
						# set state to keep track of category chosen
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.category": "personal_expenses"
							}
						}, upsert=False)

						send_message(sender_id, personal_expense_categories)

					elif message_payload in expense_subcategories:
						# set state to keep track of subcategory chosen
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.subcategory": subcategory_map[message_payload]
							}
						}, upsert=False)

						# general message for any of the subcategories
						message = "Great, now please specify the amount of your expense."

						send_message(sender_id, {"text": message})

					elif message_payload == "CONTRIBUTE_GOAL":
						# indicate that goal contribute is taking place
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.goal.contribution_flow": True
							}
						}, upsert=False)

						message = "Great choice! How much would you like to contribute towards your goal?"

						send_message(sender_id, {"text": message})

					elif message_payload == "VIEW_GOAL_PROGRESS":
						continue

					continue

				if messaging_event.get("message"):
					# arbitrary message has been received
					message_text = messaging_event["message"]["text"]

					# check to see if user exists in database
					res = user_coll.find_one({"user_id": sender_id})

					log("Response: %s" % res)

					if res is None:
						# insert user in collection
						user_coll.insert({
							"user_id": sender_id,
							"is_onboarded": False,
							"current_balance": None
						})

					if res is None or not res["is_onboarded"]:
						log("starting the onboarding..")

						# check to see if goal exists in database
						goal_res = goal_coll.find_one({"user_id": sender_id})

						if goal_res is None:
							# create goal record in mongo database
							goal_coll.insert({
								"user_id": sender_id, "goal_title": None,
							 	"goal_desc": None, "goal_amount": None,
							 	"is_achieved": False,
							 	"contribution_amount": 0.0
							 })

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

							summary = "Here's a summary of your goals: Goal Title [%s], Goal Desc [%s], Goal Amount [$%s]."  \
								% (user_goal["goal_title"], user_goal["goal_desc"], user_goal["goal_amount"])

							# update the user record to complete onboarding
							user_coll.update({"user_id": sender_id}, {
								"$set": {
									"is_onboarded" : True
								}
							}, upsert=False)

							send_message(sender_id, {"text": summary})
							send_message(sender_id, main_quick_reply)

						continue


					if state_map["expense"]["flow_instantiated"]:
						# presumably last stage of expense specification
						category = state_map["expense"]["category"]
						subcategory = state_map["expense"]["subcategory"]

						trxn_coll.insert({
							"user_id": sender_id,
							"category": category,
							"subcategory": subcategory,
							"amount": float(message_text),
							"type": "expense",
							"date": dt.datetime.today().strftime("%d-%m-%Y")
						})

						# update the current balance for the user
						current_balance = user_coll.find_one({"user_id":sender_id})["current_balance"]
						user_coll.update({"user_id":sender_id}, {
							"$set": {
								"current_balance": current_balance - float(message_text)
							}
						}, upsert=False)

						# send completion messages
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.flow_instantiated": False,
								"map.expense.category": None,
								"map.expense.subcategory": None
							}
						}, upsert=False)

						# we remove the current balance refresh for now as it is failing
						main_balance["text"] = "Your balance is: %s" % user_coll.find_one({"user_id": sender_id})["current_balance"]

						completion_message = "Awesome! Here's a quick summary of your recently added expense: Category [%s], Subcategory [%s], Amount [$%s]." \
							% (state_map["expense"]["category"], state_map["expense"]["subcategory"], message_text)

						send_message(sender_id, {"text": completion_message})
						send_message(sender_id, main_balance)
						send_message(sender_id, main_carousel)

						continue

					if state_map["income"]["flow_instantiated"]:

						subcategory = state_map["income"]["subcategory"]

						trxn_coll.insert({
							"user_id": sender_id,
							"type": "income",
							"date": dt.datetime.today().strftime("%d-%m-%Y"),
							"amount": float(message_text),
							"user_id": sender_id,
							"category": "Income",
							"subcategory": subcategory
						})

						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.income.flow_instantiated": False
							}
						}, upsert=False)

						cur_balance = user_coll.find_one({"user_id": sender_id})["current_balance"]

						user_coll.update({"user_id": sender_id}, {
							"$set": {
								"current_balance": float(message_text) + float(cur_balance)
							}
						}, upsert=False)

						main_balance["text"] = "Your balance is: %s" % user_coll.find_one({"user_id": sender_id})["current_balance"]

						send_message(sender_id, income_amount_logged)
						send_message(sender_id, main_balance)
						send_message(sender_id, main_carousel)

						continue

					if state_map["goal"]["contribution_flow"]:
						# amount has been sent back - add to mongo
						contribution_amount = goal_coll.find_one({"user_id": sender_id})["contribution_amount"]

						goal_coll.update({"user_id": sender_id}, {
							"$set": {
								"contribution_amount": contribution_amount + float(message_text)
							}
						}, upsert=False)

						# subtract from current balance
						current_balance = user_coll.find_one({"user_id": sender_id})["current_balance"]

						user_coll.update({"user_id": sender_id}, {
							"$set": {
								"current_balance": current_balance - float(message_text)
							}
						}, upsert=False)

						goal_obj = goal_coll.find_one({"user_id": sender_id})

						difference = goal_obj["goal_amount"] - goal_obj["contribution_amount"]

						goal_title = goal_obj["goal_title"]

						message = "Congrats, you are now $%s away from your goal: %s!" % (difference, goal_title)

						main_balance["text"] = "Your balance is: %s" % user_coll.find_one({"user_id": sender_id})["current_balance"]

						# set contribution flow to false
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.goal.contribution_flow": False
							}
						}, upsert=False)

						send_message(sender_id, {"text": message})
						send_message(sender_id, main_balance)
						send_message(sender_id, main_carousel)

						continue

					if messaging_event["message"].get("quick_reply"):
						message_payload = messaging_event["message"]["quick_reply"]["payload"]

						if message_payload == "SEE_BALANCE_YES":
							main_balance["text"] = "Your balance is: %s" % user_coll.find_one({"user_id": sender_id})["current_balance"]
							send_message(sender_id, main_balance)
							send_message(sender_id, main_carousel)
							continue
						if message_payload == "SEE_BALANCE_NO":
							send_message(sender_id, {"text": "Then have a nice day."})
							continue
						continue

					main_balance["text"] = "Your balance is: %s" % user_coll.find_one({"user_id": sender_id})["current_balance"]
					send_message(sender_id, main_balance)
					send_message(sender_id, main_carousel)


				if messaging_event.get("delivery"):
					# confirm delivery
					pass

				if messaging_event.get("optin"):
					# optin confirmation
					pass

	return "ok", 200


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
