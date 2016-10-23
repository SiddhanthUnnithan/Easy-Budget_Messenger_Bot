import os
import sys
import json
import datetime as dt

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
	                        "title": "",
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

	# ONBOARDING MESSAGES
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

	# EXPENSE MESSAGES

	expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "Housing Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "HOME_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Transporation Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "TRANSP_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Living Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "LIVING_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Personal Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "PERSONAL_SUBCATEGORIES"
						}
					]
				}]
			}
		}
	}

	home_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "Rent",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Rent Expense",
							"payload": "RENT_EXP_SELECTION"
						}
					]
				}, {
					"title": "Hydro",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Hydro Expense",
							"payload": "HYDRO_EXP_SELECTION"
						}
					]
				}, {
					"title": "Cable or Internet",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Cable/Internet Expense",
							"payload": "CABLE_INTERNET_EXP_SELECTION"
						}
					]
				}, {
					"title": "Phone",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Phone Expense",
							"payload": "PHONE_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}

	transportation_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "Car",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Car Expense",
							"payload": "CAR_EXP_SELECTION"
						}
					]
				}, {
					"title": "Gas",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Gas Expense",
							"payload": "GAS_EXP_SELECTION"
						}
					]
				}, {
					"title": "Parking",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Parking Expense",
							"payload": "PARKING_EXP_SELECTION"
						}
					]
				}, {
					"title": "Public Transit",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Public Transit Expense",
							"payload": "PUBLIC_TRANSIT_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}

	living_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "Food",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Food Expense",
							"payload": "FOOD_EXP_SELECTION"
						}
					]
				}, {
					"title": "Clothing",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Clothing/Laundry Expense",
							"payload": "CLOTHING_EXP_SELECTION"
						}
					]
				}, {
					"title": "Childcare",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Childcare Expense",
							"payload": "CHILDCARE_EXP_SELECTION"
						}
					]
				}, {
					"title": "Loan",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Loan Payment Expense",
							"payload": "LOAN_PAYMENT_EXP_SELECTION"
						}
					]
				}, {
					"title": "Credit Card",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Credit Card Expense",
							"payload": "CREDIT_CARD_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}

	personal_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "Recreation",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Recreation Expense",
							"payload": "RECREATION_EXP_SELECTION"
						}
					]
				}, {
					"title": "Cigarettes/Alcohol",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Cigarette/Alcohol Expense",
							"payload": "CIGARETTE_EXP_SELECTION"
						}
					]
				}, {
					"title": "Gifts/Donations",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Gift or Donation Expense",
							"payload": "GIFT_EXP_SELECTION"
						}
					]
				}, {
					"title": "Vaction/Travel",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Vacation/Travel Expense",
							"payload": "VACATION_EXP_SELECTION"
						}
					]
				}, {
					"title": "Eating Out",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Add Eating Out Expense",
							"payload": "EATING_OUT_EXP_SELECTION"
						}
					]
				}]
			}
		} 
	}

	# generate set of sub categories based on dict parsing rules - convenience
	expense_subcategories = []

	# map subcategory payload to subcategory title
	# we store title in the database
	subcategory_map = {}

	subcategory_dicts = [home_expense_categories, living_expense_categories, 
						 transportation_expense_categories,
						 personal_expense_categories]

	for elem in map(lambda x: x["attachment"]["payload"]["elements"], subcategory_dicts):
		expense_subcategories.append(elem["buttons"]["payload"])
		subcategory_map[elem["buttons"]["payload"]] = elem["title"]

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				sender_id = messaging_event["sender"]["id"]
				recipient_id = messaging_event["recipient"]["id"]

				if messaging_event.get("postback"):
					# user clicked/tapped "postback" button in earlier message
					message_payload = messaging_event["postback"]["payload"]

					if message_payload == "SET_INCOME":
						continue
					elif message_payload == "SET_EXPENSES":
						# set state to notify expense flow is instantiated
						state_coll.update({"_id": state_id}, {
							"$set": {
								"map.expense.flow_instantiated": True
							}
						}, upsert=False)

						# send all expense subcategories
						send_message(sender_id, expense_categories)

					elif message_payload == "GOAL_VISUALIZATION":
						continue
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
						})
						
						# general message for any of the subcategories
						message = "Great, now please specify the amount of your expense."

						send_message(sender_id, {"text": message})

					continue

				if messaging_event.get("message"):
					# arbitrary message has been received
					message_text = messaging_event["message"]["text"]

					# check to see if user exists in database
					res = user_coll.find_one({"user_id": sender_id})

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

						# send completion messages
						state_coll.update({"_id": state_id}, {
							"$set": {
								"flow_instantiated": False,
								"category": None,
								"subcategory": None
							}
						}, upsert=False)

						# update current balance of user
						user_coll.update({"user_id": sender_id})

						completion_message = "Awesome! Here's a quick summary of your recently added expense: Category [%s], Subcategory [%s], Amount [$%s]." \
							% (state_map["category"], state_map["subcategory"], message_text)

						send_message(sender_id, {"text": completion_message})
						send_message(sender_id, main_balance)
						send_message(sender_id, main_carousel)

						continue

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


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
