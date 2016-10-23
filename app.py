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

listUrl = 'propsercanada.com/list&'
summaryUrl = 'prospercanada.com/summary?'
statisticsUrl = 'prospercanada.com/statistic?'

user_id_url = 'userId='
category_url = '&category='
subcategory_url = '&subcategory='


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

	balance_template = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
					{
						"title": "Would you like to see your balance",
						"buttons": [
							{
								"type": "postback",
								"title": "Yes",
								"payload": "SEE_BALANCE_YES"
							},
							{
								"type": "postback",
								"title": "No",
								"payload": "SEE_BALANCE_NO"
							}
						]
					}
				]
			}
		}
	}

	main_balance = {
		"text": ""
	}

	main_carousel = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
                    "title": "Log Expenses",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Red_flag.svg/2000px-Red_flag.svg.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Add New Expense",
	                        "payload": "SET_EXPENSES"
	                    }
                    ],
                }, {
                    "title": "Log Income",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Libya_(1977-2011).svg/2000px-Flag_of_Libya_(1977-2011).svg.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Add New Income",
	                        "payload": "SET_INCOME"
	                    }
                    ],
                }, {
                    "title": "Manage Goal",
                    "image_url": "https://files.graphiq.com/2307/media/images/t2/Gold_Metallic_1395343.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Contribute To Goal",
	                        "payload": "CONTRIBUTE_GOAL"
	                    },
	                    {
	                    	"type": "postback",
	                    	"title": "View Goal Progress",
	                    	"payload": "VIEW_GOAL_PROGRESS"
	                    }
                    ],
                }, {
                	"title": "View Progress",
                	"image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Color-blue.JPG",
                	"buttons": [
						{
							"type": "postback",
							"title": "View Progress",
							"payload": "TRXN_CAROUSEL"
						}
                	]
                }]
			}
		}
	}

	income_category_carousel = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
                    "title": "Wages",
                    "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Net Income from wages",
	                        "payload": "SET_WAGES_INCOME"
	                    }
                    ],
                }, {
                    "title": "Benefits",
                    "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "Government Benefits",
	                        "payload": "SET_BENEFITS_INCOME"
	                    }
                    ],
                },
                {
                	"title": "Self-business",
                	"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                	"buttons": [
                		{
                			"type": "postback",
                			"title": "Self employment income",
                			"payload": "SET_SELF_BUSINESS_INCOME"
                		}
                	]
                },
				{
                	"title": "Other",
                	"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                	"buttons": [
                		{
                			"type": "postback",
                			"title": "Other Income sources",
                			"payload": "SET_OTHER_INCOME"
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
					"title": "Vacation/Travel",
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



	progress_trxn_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "Transaction List",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "LIST_VISUALIZATION"
						}
					]
				}, {
					"title": "General Progress",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "SUMMARY_VISUALIZATION"
						}
					]
				}, {
					"title": "All Category",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "ALL_CAT_VISUALIZATION"
						}
					]
				}, {
					"title": "Income",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "PROGRESS_INCOME_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Housing Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "PROGRESS_HOME_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Transporation Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "PROGRESS_TRANSP_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Living Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "PROGRESS_LIVING_SUBCATEGORIES"
						}
					]
				}, {
					"title": "Personal Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "Explore Sub-Categories",
							"payload": "PROGRESS_PERSONAL_SUBCATEGORIES"
						}
					]
				}]
			}
		}
	}

	progress_home_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "All Home Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "HOME_VISUALIZATION"
						}
					]
				}, {
					"title": "Rent",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_RENT_EXP_SELECTION"
						}
					]
				}, {
					"title": "Hydro",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_HYDRO_EXP_SELECTION"
						}
					]
				}, {
					"title": "Cable or Internet",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_ABLE_INTERNET_EXP_SELECTION"
						}
					]
				}, {
					"title": "Phone",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_PHONE_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}

	progress_transportation_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "All Transportation Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "TRANSPORTATION_VISUALIZATION"
						}
					]
				}, {
					"title": "Car",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_CAR_EXP_SELECTION"
						}
					]
				}, {
					"title": "Gas",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_GAS_EXP_SELECTION"
						}
					]
				}, {
					"title": "Parking",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_PARKING_EXP_SELECTION"
						}
					]
				}, {
					"title": "Public Transit",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_PUBLIC_TRANSIT_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}

	progress_living_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "All Living Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "LIVING_VISUALIZATION"
						}
					]
				}, {
					"title": "Food",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_FOOD_EXP_SELECTION"
						}
					]
				}, {
					"title": "Clothing",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_CLOTHING_EXP_SELECTION"
						}
					]
				}, {
					"title": "Childcare",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_CHILDCARE_EXP_SELECTION"
						}
					]
				}, {
					"title": "Loan",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_LOAN_PAYMENT_EXP_SELECTION"
						}
					]
				}, {
					"title": "Credit Card",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_CREDIT_CARD_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}

	progress_personal_expense_categories = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
					"title": "All Personal Expenses",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PERSONAL_VISUALIZATION"
						}
					]
				}, {
					"title": "Recreation",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_RECREATION_EXP_SELECTION"
						}
					]
				}, {
					"title": "Cigarettes/Alcohol",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_CIGARETTE_EXP_SELECTION"
						}
					]
				}, {
					"title": "Gifts/Donations",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_GIFT_EXP_SELECTION"
						}
					]
				}, {
					"title": "Vacation/Travel",
					"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_VACATION_EXP_SELECTION"
						}
					]
				}, {
					"title": "Eating Out",
					"image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
					"buttons": [
						{
							"type": "postback",
							"title": "View",
							"payload": "PROGRESS_EATING_OUT_EXP_SELECTION"
						}
					]
				}]
			}
		}
	}
	progress_income_category_carousel = {
		"attachment": {
			"type": "template",
			"payload": {
				"template_type": "generic",
				"elements": [
				{
                    "title": "All Income",
                    "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "View",
	                        "payload": "INCOME_VISUALIZATION"
	                    }
                    ],
                }, {
                    "title": "Wages",
                    "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "View",
	                        "payload": "PROGRESS_SET_WAGES_INCOME"
	                    }
                    ],
                }, {
                    "title": "Benefits",
                    "image_url": "http://messengerdemo.parseapp.com/img/gearvr.png",
                    "buttons": [
	                    {
	                        "type": "postback",
	                        "title": "View",
	                        "payload": "PROGRESS_SET_BENEFITS_INCOME"
	                    }
                    ],
                },
                {
                	"title": "Self-business",
                	"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                	"buttons": [
                		{
                			"type": "postback",
                			"title": "View",
                			"payload": "PROGRESS_SET_SELF_BUSINESS_INCOME"
                		}
                	]
                },
				{
                	"title": "Other",
                	"image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                	"buttons": [
                		{
                			"type": "postback",
                			"title": "View",
                			"payload": "PROGRESS_SET_OTHER_INCOME"
                		}
                	]
                }]
			}
		}
	}

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
						trxn_coll.insert({
							"user_id": sender_id,
							"type": "income",
							"date": dt.datetime.today().strftime("%d-%m-%Y"),
							"user_id": sender_id,
							"category": "Income",
							"subcategory": "Wages"
						})

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_BENEFITS_INCOME":
						trxn_coll.insert({
							"user_id": sender_id,
							"type": "income",
							"date": dt.datetime.today().strftime("%d-%m-%Y"),
							"user_id": sender_id,
							"category": "Income",
							"subcategory": "Benefits"
						})

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_SELF_BUSINESS_INCOME":
						trxn_coll.insert({
							"user_id": sender_id,
							"type": "income",
							"date": dt.datetime.today().strftime("%d-%m-%Y"),
							"user_id": sender_id,
							"category": "Income",
							"subcategory": "Self Business"
						})

						send_message(sender_id, income_amount_prompt)

					elif message_payload == "SET_OTHER_INCOME":
						trxn_coll.insert({
							"user_id": sender_id,
							"type": "income",
							"date": dt.datetime.today().strftime("%d-%m-%Y"),
							"user_id": sender_id,
							"category": "Income",
							"subcategory": "Other"
						})

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

					elif message_payload == "LIST_VISUALIZATION":
						send_message(sender_id, {"text": "List visualization: " + listUrl + user_id_url + sender_id})

					elif message_payload == "SUMMARY_VISUALIZATION":
						send_message(sender_id, {"text": "Summary visualization: " + summaryUrl + user_id_url + sender_id})

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
						send_message(sender_id, {"text": "Goal progress: http://google.com"})

					elif message_payload == "TRXN_CAROUSEL":
						send_message(sender_id, progress_trxn_categories)
					elif message_payload == "PROGRESS_INCOME_SUBCATEGORIES":
						send_message(sender_id, progress_income_category_carousel)
					elif message_payload == "PROGRESS_HOME_SUBCATEGORIES":
						send_message(sender_id, progress_home_expense_categories)
					elif message_payload == "PROGRESS_TRANSP_SUBCATEGORIES":
						send_message(sender_id, progress_transportation_expense_categories)
					elif message_payload == "PROGRESS_LIVING_SUBCATEGORIES":
						send_message(sender_id, progress_living_expense_categories)
					elif message_payload == "PROGRESS_PERSONAL_SUBCATEGORIES":
						send_message(sender_id, progress_personal_expense_categories)
					elif message_payload == "ALL_CAT_VISUALIZATION":
						send_message(sender_id, {"text": "All Category progress: " + listUrl + user_id_url + sender_id})
					elif message_payload == "HOME_VISUALIZATION":
						send_message(sender_id, {"text": "Home Category progress: " + listUrl + user_id_url + sender_id + category_url + "housing_expenses"})
					elif message_payload == "TRANSPORTATION_VISUALIZATION":
						send_message(sender_id, {"text": "Transportation Category progress: " + listUrl + user_id_url + sender_id + category_url + "transportation_expenses"})
					elif message_payload == "LIVING_VISUALIZATION":
						send_message(sender_id, {"text": "Living Category progress: " + listUrl + user_id_url + sender_id + category_url + "living_expenses"})
					elif message_payload == "PERSONAL_VISUALIZATION":
						send_message(sender_id, {"text": "Personal Category progress: " + listUrl + user_id_url + sender_id + category_url + "personal_expenses"})
					elif message_payload == "INCOME_VISUALIZATION":
						send_message(sender_id, {"text": "Income Category progress: " + listUrl + user_id_url + sender_id + category_url + "Income"})
					elif message_payload == "PROGRESS_RENT_EXP_SELECTION":
						send_message(sender_id, {"text": "Rent progress: " + listUrl + user_id_url + sender_id + category_url + "housing_expenses" + subcategory_url + "rent"})
					elif message_payload == "PROGRESS_HYDRO_EXP_SELECTION":
						send_message(sender_id, {"text": "Hydro progress: " + listUrl + user_id_url + sender_id + category_url + "housing_expenses" + subcategory_url + "hydro"})
					elif message_payload == "PROGRESS_ABLE_INTERNET_EXP_SELECTION":
						send_message(sender_id, {"text": "Internet progress: " + listUrl + user_id_url + sender_id + category_url + "housing_expenses" + subcategory_url + "internet"})
					elif message_payload == "PROGRESS_PHONE_EXP_SELECTION":
						send_message(sender_id, {"text": "Phone progress: " + listUrl + user_id_url + sender_id + category_url + "housing_expenses" + subcategory_url + "phone"})
					elif message_payload == "PROGRESS_CAR_EXP_SELECTION":
						send_message(sender_id, {"text": "Car progress: " + listUrl + user_id_url + sender_id + category_url + "transportation_expenses" + subcategory_url + "car"})
					elif message_payload == "PROGRESS_GAS_EXP_SELECTION":
						send_message(sender_id, {"text": "Gas progress: " + listUrl + user_id_url + sender_id + category_url + "transportation_expenses" + subcategory_url + "gas"})
					elif message_payload == "PROGRESS_PARKING_EXP_SELECTION":
						send_message(sender_id, {"text": "Parking progress: " + listUrl + user_id_url + sender_id + category_url + "transportation_expenses" + subcategory_url + "parking"})
					elif message_payload == "PROGRESS_PUBLIC_TRANSIT_EXP_SELECTION":
						send_message(sender_id, {"text": "Public Transit progress: " + listUrl + user_id_url + sender_id + category_url + "transportation_expenses" + subcategory_url + "public_transit"})
					elif message_payload == "PROGRESS_FOOD_EXP_SELECTION":
						send_message(sender_id, {"text": "Food progress: " + listUrl + user_id_url + sender_id + category_url + "living_expenses" + subcategory_url + "food"})
					elif message_payload == "PROGRESS_CLOTHING_EXP_SELECTION":
						send_message(sender_id, {"text": "Clothing progress: " + listUrl + user_id_url + sender_id + category_url + "living_expenses" + subcategory_url + "clothing"})
					elif message_payload == "PROGRESS_CHILDCARE_EXP_SELECTION":
						send_message(sender_id, {"text": "Childcare progress: " + listUrl + user_id_url + sender_id + category_url + "living_expenses" + subcategory_url + "childcare"})
					elif message_payload == "PROGRESS_LOAN_PAYMENT_EXP_SELECTION":
						send_message(sender_id, {"text": "Loan Payment progress: " + listUrl + user_id_url + sender_id + category_url + "living_expenses" + subcategory_url + "loan_payment"})
					elif message_payload == "PROGRESS_CREDIT_CARD_EXP_SELECTION":
						send_message(sender_id, {"text": "Credit Card progress: " + listUrl + user_id_url + sender_id + category_url + "living_expenses" + subcategory_url + "credit_card"})
					elif message_payload == "PROGRESS_RECREATION_EXP_SELECTION":
						send_message(sender_id, {"text": "Recreation progress: " + listUrl + user_id_url + sender_id + category_url + "personal_expenses" + subcategory_url + "recreation"})
					elif message_payload == "PROGRESS_CIGARETTE_EXP_SELECTION":
						send_message(sender_id, {"text": "Cigartte progress: " + listUrl + user_id_url + sender_id + category_url + "personal_expenses" + subcategory_url + "cigarette"})
					elif message_payload == "PROGRESS_GIFT_EXP_SELECTION":
						send_message(sender_id, {"text": "Gift progress: " + listUrl + user_id_url + sender_id + category_url + "personal_expenses" + subcategory_url + "gift"})
					elif message_payload == "PROGRESS_VACATION_EXP_SELECTION":
						send_message(sender_id, {"text": "Vacation progress: " + listUrl + user_id_url + sender_id + category_url + "personal_expenses" + subcategory_url + "vacation"})
					elif message_payload == "PROGRESS_EATING_OUT_EXP_SELECTION":
						send_message(sender_id, {"text": "Eating Out progress: " + listUrl + user_id_url + sender_id + category_url + "personal_expenses" + subcategory_url + "eating_out"})
					elif message_payload == "PROGRESS_SET_WAGES_INCOME":
						send_message(sender_id, {"text": "Wages progress: " + listUrl + user_id_url + sender_id + category_url + "Income" + subcategory_url + "Wages"})
					elif message_payload == "PROGRESS_SET_BENEFITS_INCOME":
						send_message(sender_id, {"text": "Benefits progress: " + listUrl + user_id_url + sender_id + category_url + "Income" + subcategory_url + "Benefits"})
					elif message_payload == "PROGRESS_SET_SELF_BUSINESS_INCOME":
						send_message(sender_id, {"text": "Self-business progress: " + listUrl + user_id_url + sender_id + category_url + "Income" + subcategory_url + "Self Business"})
					elif message_payload == "PROGRESS_SET_OTHER_INCOME":
						send_message(sender_id, {"text": "Other progress: " + listUrl + user_id_url + sender_id + category_url + "Income" + subcategory_url + "Other"})

					continue

					if message_payload == "SEE_BALANCE_YES":
						main_balance["text"] = "Your balance is: %s" % user_coll.find_one({"user_id": sender_id})["current_balance"]
						send_message(sender_id, main_balance)
						send_message(sender_id, main_carousel)
						continue
					if message_payload == "SEE_BALANCE_NO":
						send_message(sender_id, {"text": "Then have a nice day."})
						continue

				if messaging_event.get("message"):
					# arbitrary message has been received
					message_text = messaging_event["message"]["text"]

					# check to see if user exists in database
					res = user_coll.find_one({"user_id": sender_id})

					send_message(sender_id, thisIsATest)

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

						trxn_coll.update({"user_id": sender_id}, {
							"$set": {
								"amount": float(message_text)
							}
						}, upsert=False)

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

					send_message(sender_id, balance_template)

				if messaging_event.get("delivery"):
					# confirm delivery
					pass

				if messaging_event.get("optin"):
					# optin confirmation
					pass



	return "ok", 200


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
