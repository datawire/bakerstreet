#!/usr/bin/env python

import sys
import threading
import uuid

from flask import Flask, jsonify
app = Flask(__name__)

index = 0
service_id = uuid.uuid4()

def synchronized(func):
    func.__lock__ = threading.Lock()

    def synchronized_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return synchronized_func

@synchronized
def increment_index():
    global index
    index += 1

@app.route("/")
def hello():
    increment_index()
    return jsonify(service_id=str(service_id), index=index, message="Hello, world!")

@app.route("/health")
def health_check():
    increment_index()
    return jsonify(service_id=str(service_id), index=index, status='OK')

if __name__ == "__main__":
    passed_args = sys.argv
    app.run(port=int(passed_args[1]), host="0.0.0.0")
