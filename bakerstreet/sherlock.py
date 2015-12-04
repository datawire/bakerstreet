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

import bakerstreet
import logging
import quark_twisted_runtime

from docopt import docopt
from humanfriendly import parse_timespan
from hub.message import AddServiceEndpoint
from hub.model import *
from hub import RegistryClient
from twisted.internet import reactor
from urlparse import urlparse

class HAProxyConfigRewriter(object):
    pass

class Sherlock(object):
    pass

def run_sherlock(args):
    config = bakerstreet.load_config(args['--config'])['sherlock']
    pass

def main():
    exit(run_sherlock(docopt(__doc__, version="sherlock {0}".format("dev"))))

if __name__ == "__main__":
    main()
