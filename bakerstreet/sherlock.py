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

"""Sherlock

Usage:
    sherlock [options]
    sherlock (-h | --help)
    sherlock --version

Options:
    -c --config=<path>  Set the path of the Sherlock configuration file [default: /etc/datawire/sherlock.yml]
    -h --help           Show the help.
    --version           Show the version.
"""

import hashlib
import json
import logging
import quark_twisted_runtime
import _metadata

from bakerstreet import *
from abc import abstractmethod
from docopt import docopt
from hub.client import *
from hub.message import Subscribe
from subprocess import Popen
from time import time, ctime
from twisted.internet import reactor


class ConfigRewriter(object):

    @abstractmethod
    def render(self, services):
        pass

    @abstractmethod
    def write(self, services):
        pass


class HAProxyConfigRewriter(ConfigRewriter):

    def __init__(self, haproxy_config):
        self.logger = logging.getLogger('sherlock')
        self.current_haproxy_config_checksum = None
        self.haproxy_executable = haproxy_config['executable']
        self.haproxy_run_dir = haproxy_config['run_dir']
        self.haproxy_reload_cmd = haproxy_config['reload_command']
        self.haproxy_config_template_path = haproxy_config['config_template']
        self.haproxy_config_path = os.path.join(self.haproxy_run_dir, 'haproxy.conf')
        self.haproxy_pid_path = haproxy_config['pid_path']

    @staticmethod
    def rendered_checksum(content):
        md5 = hashlib.md5()
        md5.update(content)
        return md5.hexdigest()

    @staticmethod
    def reqrep_line(name, path):
        return "    reqrep ^([^\ :]*)\ /{}(.*) \\1\ {}\\2".format(name, path if path else "/")

    @staticmethod
    def server_line(endpoint):
        name = "{}_{}".format(endpoint['address'], endpoint['port'])
        return "    server {} {}:{} maxconn 32".format(name, endpoint['address'], endpoint['port'])

    def read_template(self):
        with open(self.haproxy_config_template_path, 'r') as template:
            return template.read()

    def render(self, services):
        frontends, backends = [], []
        for name, endpoints in services.iteritems():
            if endpoints:
                backend = "BE_" + name
                acl_name = "IS_" + name

                acl = "\n    acl {} path_beg /{}".format(acl_name, name)
                acl_to_backend = "    use_backend {} if {}".format(backend, acl_name)

                frontends.append(acl)
                frontends.append(acl_to_backend)
                backends.append("\n backend {}".format(backend))

                # Rewrites the incoming URL so that the service name is removed and replaced with the service path.
                path = None  # todo: rethink
                backends.append(HAProxyConfigRewriter.reqrep_line(name, path))

                for endpoint in endpoints:
                    if endpoint['scheme'] == 'http':
                        backends.append(HAProxyConfigRewriter.server_line(endpoint))

            else:
                self.logger.warn("Received service without any routes (service: %s)", name)

        result = self.read_template()
        result += "\n".join(frontends + backends)

        return result, self.rendered_checksum(result)

    def write(self, services):
        rendered, checksum = self.render(services)

        if checksum != self.current_haproxy_config_checksum:
            self.current_haproxy_config_checksum = checksum

            with open(self.haproxy_config_path, "wb+") as conf:
                conf.write("# Last update %s\n" % ctime())
                conf.write(rendered)
                conf.write("\n")

            if self.haproxy_executable is not None:
                command = self.haproxy_executable + " "
                try:
                    command += self.haproxy_reload_cmd.format(self.haproxy_config_path, open(self.haproxy_pid_path).read())
                except IOError as e:
                    self.logger.error("Error reading HAProxy PID file (msg: %s)", e.message)

                try:
                    proc = Popen(command.split(), close_fds=True)
                    proc.wait()

                    self.logger.info("Succeeded launching (program: %s, pid: %s)", self.haproxy_executable, proc.pid)
                except OSError as exc:
                    self.logger.error("Failed launching (program: %s)", self.haproxy_executable, proc.pid)
            else:
                self.logger.debug("HAProxy executable is not defined; Skipping reload")
        else:
            self.logger.debug("No HAProxy config changes detected (checksum: {})", checksum)


class Sherlock(HubClient):

    def __init__(self, runtime, gateway_options, rewriter, config):
        HubClient.__init__(self, runtime, gateway_options)
        self.runtime = runtime
        self.config = config
        self.rewriter = rewriter
        self.services = {}
        self.debounce = 10
        self.update_received = False
        self.update_received_time = None

    def onConnected(self, connect):
        print("connected!")
        msg = Subscribe()
        self.sendMessage(msg)

    def onSynchronize(self, message):
        update = json.loads(message.data).get('services', {})

        self.update_received = self.services != update
        if self.update_received:
            self.services = update
            self.update_received_time = time()

        self.schedule(3.0)

    def run(self):
        self.scheduleNow()

        if not self.update_received:
            return

    def onExecute(self, runtime):
        if not self.isConnected():
            self.connect()
            return

        if not self.update_received:
            return

        elapsed = time() - self.update_received_time
        if elapsed < self.debounce:
            self.runtime.schedule(self, self.debounce)
            return

        self.rewriter.write(self.services)


def run_sherlock(args):
    config = load_config(args['--config'])['sherlock']

    runtime = quark_twisted_runtime.get_runtime()
    rewriter = HAProxyConfigRewriter(config['haproxy'])

    gateway_options = get_gateway_options(config['hub_gateway'])

    sherlock = Sherlock(runtime, gateway_options, rewriter, config)
    sherlock.run()
    reactor.run()


def main():
    exit(run_sherlock(docopt(__doc__, version="sherlock {0}".format(_metadata.__version__))))


if __name__ == "__main__":
    main()
