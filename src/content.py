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
    "text": ""
}

colour_map = {
    "red": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Red_flag.svg/2000px-Red_flag.svg.png",
    "green": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Libya_(1977-2011).svg/2000px-Flag_of_Libya_(1977-2011).svg.png",
    "gold": "https://files.graphiq.com/2307/media/images/t2/Gold_Metallic_1395343.png",
    "blue": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Color-blue.JPG"
}

main_carousel = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": [
            {
                "title": "Log Expenses",
                "image_url": colour_map["red"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add New Expense",
                        "payload": "SET_EXPENSES"
                    }
                ],
            }, {
                "title": "Log Income",
                "image_url": colour_map["green"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add New Income",
                        "payload": "SET_INCOME"
                    }
                ],
            }, {
                "title": "Manage Goal",
                "image_url": colour_map["gold"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Contribute To Goal",
                        "payload": "CONTRIBUTE_GOAL"
                    }
                ],
            }, {
                "title": "Progress",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Track Your Progress",
                        "payload": "VIEW_GEN_PROGRESS"
                    }
                ]
            }]
        }
    }
}

income_map = {
    "SET_WAGES_INCOME": "Wages",
    "SET_BENEFITS_INCOME": "Benefits",
    "SET_SELF_BUSINESS_INCOME": "Self Business",
    "SET_OTHER_INCOME": "Other"
}

income_category_carousel = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": [
            {
                "title": "Wages",
                "image_url": colour_map["green"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Net Income from wages",
                        "payload": "SET_WAGES_INCOME"
                    }
                ],
            }, {
                "title": "Benefits",
                "image_url": colour_map["green"],
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
                "image_url": colour_map["green"],
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
                "image_url": colour_map["green"],
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
    "text": "Perfect, for final touches I'm going to need you to enter your current balance."
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
                "image_url": colour_map["red"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Explore Sub-Categories",
                        "payload": "HOME_SUBCATEGORIES"
                    }
                ]
            }, {
                "title": "Transporation Expenses",
                "image_url": colour_map["red"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Explore Sub-Categories",
                        "payload": "TRANSP_SUBCATEGORIES"
                    }
                ]
            }, {
                "title": "Living Expenses",
                "image_url": colour_map["red"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Explore Sub-Categories",
                        "payload": "LIVING_SUBCATEGORIES"
                    }
                ]
            }, {
                "title": "Personal Expenses",
                "image_url": colour_map["red"],
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
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Rent Expense",
                        "payload": "RENT_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Hydro",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Hydro Expense",
                        "payload": "HYDRO_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Cable or Internet",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Cable/Internet Expense",
                        "payload": "CABLE_INTERNET_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Phone",
                "image_url": colour_map["blue"],
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
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Car Expense",
                        "payload": "CAR_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Gas",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Gas Expense",
                        "payload": "GAS_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Parking",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Parking Expense",
                        "payload": "PARKING_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Public Transit",
                "image_url": colour_map["blue"],
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
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Food Expense",
                        "payload": "FOOD_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Clothing",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Clothing/Laundry Expense",
                        "payload": "CLOTHING_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Childcare",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Childcare Expense",
                        "payload": "CHILDCARE_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Loan",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Loan Payment Expense",
                        "payload": "LOAN_PAYMENT_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Credit Card",
                "image_url": colour_map["blue"],
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
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Recreation Expense",
                        "payload": "RECREATION_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Cigarettes/Alcohol",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Cigarette/Alcohol Expense",
                        "payload": "CIGARETTE_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Gifts/Donations",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Gift or Donation Expense",
                        "payload": "GIFT_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Vacation/Travel",
                "image_url": colour_map["blue"],
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Add Vacation/Travel Expense",
                        "payload": "VACATION_EXP_SELECTION"
                    }
                ]
            }, {
                "title": "Eating Out",
                "image_url": colour_map["blue"],
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
