# Easy Budget Messenger Chat Bot

The Remember-The-Interns team is happy to present Prosper Canada's 'Easy Budget' Messenger chat bot!

Through the 'Easy Budget' bot, individuals are able to log and track their income and expenses within the comfort and familiarity of Facebook Messenger.

## Deployment
The Flask server is deployed on Heroku, and has been configured to work with an existing Facebook Page and Application.

To use this code, you will need to create a Facebook Page and register a Messenger Application to connect to that page.

From Facebook you will need to generate a 'PAGE_ACCESS_TOKEN' and add it to your Heroku environment (i.e. as an environment variable).

As well, you will need to add a 'VERIFY_TOKEN' environment variable to Heroku.

On your Facebook Application you will then need to set up a Webhook with your 'VERIFY_TOKEN' value and your Heroku application host name. Please use the following subscription events: messages, message-postbacks.
