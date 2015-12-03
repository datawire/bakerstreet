# Copyright 2015 Datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""hudson

Hudson is a tiny HTTP service that is useful for sanity testing Watson and Sherlock.

Usage:
    hudson [options]
    hudson (-h | --help)
    hudson --version

Options:
    -b --bind=<addr>    Set the internet address to bind to [default: 127.0.0.1]
    -p --port=<num>     Set the port to listen on [default: 2218]
    -h --help           Show the help.
    --version           Show the version.
"""

import json
import logging
import uuid

from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler

from docopt import docopt

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('--->  %(levelname)s: %(name)s - %(asctime)s - %(message)s'))

logger = logging.getLogger('hudson')
logger.addHandler(ch)

service_id = uuid.uuid4()

class MrsHudsonHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        content_type = 'application/json; charset=utf-8'

        if self.path == "/" or self.path == "":
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.wfile.write('\n')
            json.dump({'service_id': str(service_id), 'msg': 'Hello, world!'}, self.wfile)
        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.wfile.write('\n')
            json.dump({'service_id': str(service_id)}, self.wfile)
        else:
            self.send_response(404)


def run_hudson(args):
    logger.setLevel('INFO')
    logger.info('starting hudson (bind: %s, port: %s)', args['--bind'], int(args['--port']))
    server = HTTPServer((args['--bind'], int(args['--port'])), MrsHudsonHandler)
    server.serve_forever()

def main():
    exit(run_hudson(docopt(__doc__, version="hudson {0}".format("dev"))))

if __name__ == "__main__":
    main()
