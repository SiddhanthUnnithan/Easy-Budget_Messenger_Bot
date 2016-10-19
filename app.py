from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

def sub():
	return pd.DataFrame([1,2,3])

@app.route("/")
def hello_world():
	return "hello world"

@app.route("/test")
def test():
	data = sub()[0].tolist()
	return jsonify(values=data)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
