#!/usr/bin/env python

import sys
import threading

from flask import Flask, jsonify, request
from pprint import pprint
app = Flask(__name__)

index = 0
service_id = "bakerscale_stats"

stats = {
    'watson': {},
    'sherlock': {},
    'directory': {}
}

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

@app.route("/health")
def health_check():
    increment_index()
    return jsonify(service_id=service_id, index=index, status='OK')

@app.route("/stats")
def get_stats():
    return jsonify(stats)

@app.route("/sherlocks/<sherlock>/stats", methods=['PUT'])
def add_latencies(sherlock):
    if sherlock not in stats['sherlock']:
        stats['sherlock'][sherlock] = {
            'routes': 0,
            'latencies': []
        }

    sherlock_stats = request.get_json(force=True)
    stats['sherlock'][sherlock]['routes'] = int(sherlock_stats['routes'])
    stats['sherlock'][sherlock]['latencies'].extend(sherlock_stats['latencies'])

    return '', 204


if __name__ == "__main__":
    passed_args = sys.argv
    app.run(port=int(passed_args[1]), host="0.0.0.0")
