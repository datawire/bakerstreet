#!/usr/bin/env python

from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def hello_generic():
    return "Hi, everybody!"

@app.route("/health")
def health_check():
    return "Healthy!"

@app.route("/hello")
def hello_name():
    name = request.args.get('name')
    return "Hi, %s!" % name

if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0")
