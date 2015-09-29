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
    sherlock --config=<file>
    sherlock (-h | --help)
    sherlock --version

Options:
    -h --help       Show the help.
    --version       Show the version.
    -c --config     Set the path of the Watson configuration file
"""

import _metadata

from docopt import docopt

def main(args):
    pass

def call_main():
    exit(main(docopt(__doc__, version="sherlock {0}".format(_metadata.__version__))))

if __name__ == "__main__":
    call_main()
