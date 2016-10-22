from flask import Flask, jsonify
# import pandas as pd
from pymongo import MongoClient
import psycopg2

app = Flask(__name__)

ec2_ip = '54.224.111.118'

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


@app.route("/")
def hello_world():
	return "hello world"

#
# @app.route("/test")
# def test():
# 	data = pd.DataFrame([1,2,3])[0].tolist()
# 	return jsonify(values=data)


@app.route("/mongotest")
def mongo():
	res = mongocmd()
	return jsonify(author=res['author'], text=res['text'])


@app.route("/pgtest")
def postgres():
	res = postgrescmd()
	return jsonify(author=res['author'], message=res['message'])


if __name__ == "__main__":
	app.run(port=5000, debug=True)
