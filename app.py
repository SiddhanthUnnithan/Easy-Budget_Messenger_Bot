import os
import sys
import json

import requests
from flask import Flask, jsonify, request

from pymongo import MongoClient
import psycopg2

app = Flask(__name__)

ec2_ip = '54.224.111.118'

# HELPERS
def log(message):
	print(str(message))
	sys.stdout.flush()


def send_message(recipient_id, message_text):
	log("sending message to %s: %s" % (recipient_id, message_text))

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
        "message": {
            "text": message_text
        }
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

	if data["object"] == "page":

		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				if messaging_event.get("message"):
					# message has been received
					sender_id = messaging_event["sender"]["id"]
					recipient_id = messaging_event["recipient"]["id"]
					message_text = messaging_event["message"]["text"]

					send_message(sender_id, "Yo!")

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

#
# @app.route("/test")
# def test():
# 	data = pd.DataFrame([1,2,3])[0].tolist()
# 	return jsonify(values=data)


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
