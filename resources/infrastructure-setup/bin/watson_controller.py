#!/usr/bin/env python

import json
import yaml
import glob
import os
import subprocess
import signal
import atexit

from argparse import ArgumentParser
from flask import Flask, Response, request
app = Flask(__name__)

# path where datawire configuration is stored
DATAWIRE_CONFIG_ROOT = None

# path where the Watson executable is located
WATSON_EXECUTABLE_PATH = None

# dictionary of configurations to Watson PIDs.
WATSON_INSTANCES = dict()

def get_known_watson_configs():
    configs = glob.glob('%s/watson-*.conf' % DATAWIRE_CONFIG_ROOT)
    return map(lambda s: s.replace("%s/" % DATAWIRE_CONFIG_ROOT, ''), configs)

def kill_subprocess(pid):
    try:
        os.kill(int(pid), signal.SIGKILL)
    except OSError:
        pass
    os.waitpid(int(pid), 0)

@atexit.register
def kill_all_watson_instances():
    app.logger.info("Terminating all running watson instances...")
    for name, pid in WATSON_INSTANCES.iteritems():
        kill_subprocess(pid)
        WATSON_INSTANCES.pop(name, None)

@app.route('/watsons/configs')
def list_known_watson_configs():
    return Response(response=json.dumps(get_known_watson_configs()), status=200, mimetype='application/json')

@app.route('/watsons/<name>')
def get_watson_info(name):
    resp = Response(status=404)

    if name in WATSON_INSTANCES:
        resp = Response(response=json.dumps(dict(watson_pid=WATSON_INSTANCES.get(name))), status=200, mimetype="application/json")

    return resp

@app.route('/watsons/<name>', methods=['DELETE'])
def kill_watson(name):
    pid = WATSON_INSTANCES.get(name, None)
    if pid is not None:
        kill_subprocess(pid)
        WATSON_INSTANCES.pop(name, None)

    return Response(status=200)

@app.route('/watsons', methods=['GET'])
def show_watsons():
    return Response(response=json.dumps(dict(WATSON_INSTANCES)), status=200, mimetype='application/json')

@app.route('/watsons', methods=['POST'])
def start_watson():
    config_name = request.args.get('config_name')
    if config_name not in get_known_watson_configs():
        print get_known_watson_configs()
        print "no config (name: %s)" % config_name
        return Response(status=400)

    if config_name in WATSON_INSTANCES:
        print "already loaded"
        return Response(status=400)

    try:
        proc = subprocess.Popen(["%s" % WATSON_EXECUTABLE_PATH,
                                 "-c", "/etc/datawire/%s" % config_name])

        pid = int(proc.pid)
        print "loaded (pid: %s)" % pid
        WATSON_INSTANCES[config_name] = int(pid)
        return Response(status=200)
    except Exception as e:
        app.logger.error(e)
        return Response(status=500)


@app.route('/info')
def info():
    return Response(response=json.dumps(dict(datawire_config_root=DATAWIRE_CONFIG_ROOT,
                                             watson_executable_path=WATSON_EXECUTABLE_PATH)),
                    status=200,
                    mimetype='application/json')


def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", help="read from additional config file", metavar="FILE")
    args = parser.parse_args()

    config = None
    with open(args.config, 'r') as stream:
        config = yaml.load(stream)

    global DATAWIRE_CONFIG_ROOT
    DATAWIRE_CONFIG_ROOT = config['datawire_config_root']

    global WATSON_EXECUTABLE_PATH
    WATSON_EXECUTABLE_PATH = config['watson_executable_path']

    app.run(debug=True,
            host=config['watson_controller_listen_address'],
            port=int(config['watson_controller_port']))

if __name__ == "__main__":
    main()

