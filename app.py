from flask import Flask, jsonify
import pandas as pd
import pymongo

app = Flask(__name__)

def mongoconnect():
	client = MongoClient('<ec2-instance_ip>', 27017)
	db = client.test
	coll = db.coll

	# test an insertion
	test_post = {'author': 'Sid', 'text': 'hello_world'}
	uid = coll.insert_one(test_post).inserted_id

	# test a retrieval
	res = coll.find_one("_id":uid)

	if res is None:
		return "Empty result set."

	return res


@app.route("/")
def hello_world():
	return "hello world"


@app.route("/test")
def test():
	data = pd.DataFrame([1,2,3])[0].tolist()
	return jsonify(values=data)


@app.route("/mongotest")
def mongo():
	res = mongoconnect()
	return jsonify(author=res['author'], text=res['text'])


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
