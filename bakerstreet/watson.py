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

"""Watson

Usage:
    watson --config=FILE
    watson (-h | --help)
    watson --version

Options:
    --config=FILE   Load the specified Watson config file.
    -h --help       Show the help.
    --version       Show the version.
"""

import _metadata

from datawire import Configuration, Tether
from docopt import docopt
from proton.reactor import Reactor

class HTTPHealthCheck(object):

    def __init__(self, method, url, healthy_status_codes):
        self.method = HTTPHealthCheck.__validate_http_method_is_allowed(method)
        self.url = HTTPHealthCheck.__validate_url(url)
        self.healthy_status_codes = healthy_status_codes

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        return "{0}({1} {2})".format(HTTPHealthCheck.__class__.__name__, self.method, self.url)

    @staticmethod
    def __validate_healthy_status_codes(codes):
        if not codes:
            raise ValueError("At least one HTTP status code must be defined for service health check")

        return codes

    @staticmethod
    def __validate_http_method_is_allowed(method):
        if method not in frozenset(['GET', 'HEAD']):
            raise ValueError("Unsupported HTTP method for service health check (method: {0})".format(method))
        return method

    @staticmethod
    def __validate_url(url):
        return url


class WatsonMessageHandler(object):

    def __init__(self, args, health_check, log):
        self.health_check = health_check
        self.just_started = True
        self.log = log
        self.tether = None
        self.tether_config = args.directory, args.address, args.service_url
        self.time_until_next_check = args.period
        self.url = args.service_url

    def on_reactor_init(self, event):
        event.reactor.schedule(0, self)

    def on_timer_task(self, event):

        """Checks the service Watson is responsible for to see if the service is still alive.

        :param event: the timer event triggering this check
        :return: None
        """

        if self.health_check():
            # Alive
            if self.tether is None:
                # Just came to life
                self.log.info("DEAD -> LIVE (%s)", self.url)
                self.tether = Tether(*self.tether_config)
                self.tether.start(event.reactor)
        else:
            # Dead
            if self.tether is not None:
                # Just died
                self.log.info("LIVE -> DEAD (%s)", self.url)
                self.tether.stop(event.reactor)
                self.tether = None
                self.log.debug("health check at %s for service %s", self.health_check.url, self.url)
            elif self.just_started:
                self.log.info("START -> DEAD (%s)", self.url)
                self.just_started = False
                self.log.debug("health check check at %s for service %s", self.health_check.url, self.url)

        event.reactor.schedule(self.time_until_next_check, self)

def load_config(path=None):
    pass

def main(args):
    import logging
    log = logging.getLogger(__name__)

    config = load_config(args['config'])

    health_check = HTTPHealthCheck(None, None, None)

    log.info("""Starting Watson...
                Directory Host   : %s
                Health Check     : %s
                Service URL      : %s
                Service Name     : %s""", None, health_check, None, None)
    Reactor(WatsonMessageHandler(None, health_check, log))

def call_main():
    exit(main(docopt(__doc__, version="watson {0}".format(_metadata.__version__))))

if __name__ == "__main__":
    call_main()

