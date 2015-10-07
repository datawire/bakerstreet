#!/usr/bin/env python

import sys

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
    args = sys.argv
    app.run(port=int(args[1]), host="0.0.0.0")
