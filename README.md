# Easy Budget Messenger Chat Bot

The Remember-The-Interns team is happy to present Prosper Canada's 'Easy Budget' Messenger chat bot!

Through the 'Easy Budget' bot, individuals are able to log and track their income and expenses within the comfort and familiarity of Facebook Messenger.

## Features
Goal Setting
- The application presents an underlying goal for users to set, prior to logging their income and expenses.
- The idea behind setting a goal was providing users with something to work towards, encouraging them to get into the habit of budgeting.

Income/Expense Logging
- Through simple (and directed) conversation with the bot, users are able to log income and expense streams.
- The current iteration (v0.1) of the bot segments income and expenses based on a 'Monthly Budgeting Manual' presented here: http://prospercanada.org/prospercanada/media/PDF/Facilitator%20Tools/English/Module%203/Activity_Sheet_3-5_Monthly-budget-worksheet.pdf

Goal Management
- As an instantaneous 'account balance' is not a good indicator of whether or not a user is capable of achieving their goal, we wanted to create a separate 'goal pot'.
- Through the goal management tool, users are capable of contributing towards their goal (i.e. deducting a set amount from their current balance).

## Deployment
The Flask server is deployed on Heroku, and has been configured to work with an existing Facebook Page and Application.

To use this code, you will need to create a Facebook Page and register a Messenger Application to connect to that page.

From Facebook you will need to generate a 'PAGE_ACCESS_TOKEN' and add it to your Heroku environment (i.e. as an environment variable).

As well, you will need to add a 'VERIFY_TOKEN' environment variable to Heroku.

On your Facebook Application you will then need to set up a Webhook with your 'VERIFY_TOKEN' value and your Heroku application host name. Please use the following subscription events: messages, message-postbacks.

A future iteration focus on deploying this applicationto a dedicated EC2 instance configured to support HTTPS requests.

## Backend

Node: https://github.com/AbhijithRamalingam/gift_the_code_node

Visualizer: https://github.com/kangzeroo/Prosper-Canada-Financebot-Visualizer

Mongo: The data is stored on mogno so you will require a mongo db connection and would need to provide this to the Flask application. If you check the database_files directory there are commands to run and configure a mongo3.2.7 Docker image. 
