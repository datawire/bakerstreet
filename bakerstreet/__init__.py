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

__all__ = [
    "__title__", "__summary__", "__uri__", "__version__", "__author__", "__email__", "__license__", "__copyright__"
]

__title__ = "Baker Street"
__summary__ = "Client-side load balancing for microservices"
__uri__ = "http://www.bakerstreet.io/"

__version__ = "0.6"

__author__ = "datawire.io"
__email__ = "hello@datawire.io"

__license__ = "Apache License, Version 2.0"
__copyright__ = "2015 %s" % __author__

import os
import re
import yaml

# import logging
# import logging.config
# try:
#     from logging import NullHandler
# except ImportError:
#     class NullHandler(logging.Handler):
#         def emit(self, record):
#             pass
#
# logging.getLogger(__name__).addHandler(NullHandler())

def load_config(path):

    """Reads a Baker Street configuration file.

    :param path: the path to the configuration file
    :return: a dictionary containing configuration values
    """

    # configure the yaml parser to allow grabbing OS environment variables in the config.
    pattern = re.compile(r'^(.*)<%= ENV\[\'(.*)\'\] %>(.*)$')
    yaml.add_implicit_resolver('!env_regex', pattern)

    def env_regex(loader, node):
        value = loader.construct_scalar(node)
        # var = pattern.match(value).groups()[0]
        front, variable_name, back = pattern.match(value).groups()
        return str(front) + os.environ[variable_name] + str(back)

    yaml.add_constructor('!env_regex', env_regex)

    with open(path, 'r') as stream:
        return yaml.load(stream)
