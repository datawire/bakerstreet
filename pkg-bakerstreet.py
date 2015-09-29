#!/usr/bin/env python

# Copyright 2015 The Baker Street Authors. All rights reserved.
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

from bakerstreet import _metadata
from pkg_common import Common
from roy import build, deps


class BakerStreet(Common):

    def __init__(self):
        self.arch = "all"
        self.conf = ["/etc/datawire/sherlock.conf"]
        self.build_deps = []
        self.deps = [deps.datawire, deps.haproxy, deps.policycoreutils]
        self.iteration = 1
        self.name = "datawire-bakerstreet"
        self.version = _metadata.__version__

        self.postinstall = """
/usr/sbin/setsebool -P haproxy_connect_any on || true
/usr/bin/chcon --type haproxy_var_run_t /opt/datawire/run || true
"""

    def build(self, distro):
        result = self.install_prep()
        result += """
cp bakerstreet/_metadata.py /work/install/opt/datawire/lib
"""
        result += self.install_script("")
        result += self.install_config(self.name, distro.image)
        return result

build(BakerStreet())