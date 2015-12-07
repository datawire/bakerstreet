# Copyright 2015 datawire. All rights reserved.
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

from setuptools import setup

metadata = {}
with open("bakerstreet/_metadata.py") as fp:
    exec(fp.read(), metadata)


setup(
    name='datawire-bakerstreet',
    version=metadata["__version__"],
    description=metadata["__summary__"],
    author=metadata["__author__"],
    author_email=metadata["__email__"],
    url=metadata["__uri__"],
    license=metadata["__license__"],
    packages=['bakerstreet'],
    include_package_data=True,
    install_requires=["docopt",
                      "humanfriendly",
                      "pytest",
                      "pyyaml",
                      "requests",
                      "datawire-quark-core",
                      "datawire-quark-twisted"],
    entry_points={"console_scripts": [
        "watson = watson.command:main",
        "sherlock = sherlock.command:main",
        "hudson = hudson.command:main"
    ]},
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
