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

"""watson

Usage:
    watson [options]
    watson (-h | --help)
    watson --version

Options:
    -c --config=<path>  Set the path of the Watson configuration file [default: /etc/datawire/watson.yml]
    -h --help           Show the help.
    --version           Show the version.
"""

import bakerstreet
import logging
import quark_twisted_runtime
import requests

from docopt import docopt
from humanfriendly import parse_timespan
from hub.message import AddServiceEndpoint
from hub.model import *
from hub import RegistryClient
from requests.exceptions import ConnectionError
from twisted.internet import reactor
from urlparse import urlparse


logging.getLogger("requests").setLevel(logging.WARNING)

class BaseHealthCheck(HealthCheck):

    """Base class for all health check implementations. Implementations should override the run_check method"""

    def __init__(self, logger, config):
        HealthCheck.__init__(self)
        self.logger = logger
        self.consecutive_failure_count = 0
        self.consecutive_success_count = 0
        self.seconds_until_timeout = parse_timespan(config.get('timeout', '2s'))
        self.check_url = config['url']
        self.failures_allowed = config['unhealthy_threshold']
        self.successes_required = config['healthy_threshold']

    def check(self):
        check_result = self.run_check()
        if check_result:
            self.consecutive_failure_count = 0

            if self.consecutive_success_count < self.successes_required:
                self.consecutive_success_count += 1

            return self.consecutive_success_count >= self.successes_required
        else:
            self.consecutive_success_count = 0

            if self.consecutive_failure_count < self.failures_allowed:
                self.consecutive_failure_count += 1

            return self.consecutive_failure_count < self.failures_allowed

    def run_check(self):
        return True

class HTTPHealthCheck(BaseHealthCheck):

    """A HTTP health check"""

    def __init__(self, logger, config):
        BaseHealthCheck.__init__(self, logger, config)
        self.method = config.get('method', 'GET')
        self.healthy_statuses = frozenset(config.get('healthy_statuses', frozenset({200})))

    def run_check(self):
        try:
            resp = requests.request(self.method, self.check_url, timeout=self.seconds_until_timeout)
            return resp.status_code in self.healthy_statuses
        except ConnectionError:
            return False

    @staticmethod
    def __check_method(self, method):
        # not our job to judge how someone decides to implement a health check method even if some of these do not make
        # any sense to to use in practice.
        if str(method).upper() in {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'TRACE'}:
            return True
        else:
            raise ValueError('Invalid HTTP method for health check (method: {})'.format(method))

class Watson(RegistryClient):

    """Lightweight, configurable HTTP/TCP service health checking program for use with Datawire Baker Street"""

    def __init__(self, runtime, logger, service_registry, config, health_check):
        RegistryClient.__init__(self, runtime, "localhost", 1234)

        service_config = config['service']
        health_check_config = config['health_check']
        self.endpoint = build_endpoint(service_config)

        self.first_run = True
        self.logger = logger
        self.service_registry_addr = service_registry.split(':')[0]
        self.service_registry_port = int(service_registry.split(':')[1])
        self.health_check = health_check
        self.health_check_frequency = parse_timespan(health_check_config['frequency'])
        self.service_url = service_config['url']
        self.service_name = service_config['name']

    def initialize(self):
        self.onExecute(self.runtime)

    def onRegistryJoin(self, join):
        self.send(AddServiceEndpoint(self.endpoint).toJSON().toString())

    def onExecute(self, runtime):
        if self.health_check.check():
            if not self.isConnected():
                print("DEAD -> LIVE")
                self.subscribe(self)
        else:
            if self.isConnected():
                self.disconnect()
                print("LIVE -> DEAD")
            elif self.first_run:
                print("START -> DEAD")
                self.first_run = False

        self.runtime.schedule(self, self.health_check_frequency)

def build_endpoint(service_config):
    url = urlparse(service_config['url'])
    port = ServicePort(str(url.scheme), url.port)
    addr = NetworkAddress(url.hostname, 'ipv4')
    return ServiceEndpoint(service_config['name'], addr, port)

def run_watson(args):
    config = bakerstreet.load_config(args['--config'])['watson']

    logging.basicConfig(format=config['logging']['format'], level=str(config['logging'].get('level', 'DEBUG')).upper())
    log = logging.getLogger('watson')

    health_check = HTTPHealthCheck(log, config['health_check'])
    runtime = quark_twisted_runtime.get_twisted_runtime()

    log.info('Running Watson... (for: %s)', config['service']['url'])
    watson = Watson(runtime, log, config['service_registry'], config, health_check)
    watson.initialize()

    reactor.run()

def main():
    exit(run_watson(docopt(__doc__, version="watson {0}".format("dev"))))

if __name__ == "__main__":

    main()
