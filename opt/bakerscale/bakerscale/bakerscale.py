#!/usr/bin/env python

"""bakerscale

Usage:
  bakerscale directory
  bakerscale sherlock DIRHOST
  bakerscale watson DIRHOST SVCURL SVCNAME HEALTHURL

Use localhost for the hostname in SVCURL. The launcher will replace it
with the correct externally-visible IP address.
"""

import subprocess
import os
from docopt import docopt


config_template = """
[Datawire]
directory_host: %(DIRHOST)s
"""

watson_template = """
[Watson]
service_url: %(SVCURL)s
service_name: %(SVCNAME)s
health_check_url: %(HEALTHURL)s
"""

footer = "logging: DEBUG\n"

def main(args):
    my_IP = subprocess.check_output("hostname -i".split()).split()[:1][0]
    if args["directory"]:
        args["DIRHOST"] = my_IP

    with open("bakerst.conf", "wb") as conf:
        conf.write(config_template % args)
        if args["watson"]:
            args["SVCURL"] = args["SVCURL"].replace("localhost", my_IP)
            conf.write(watson_template % args)
        conf.write(footer)

    if args["directory"]:
        os.execvp("directory", "directory -c /bakerst.conf -a //bakerscale/directory".split())
    elif args["sherlock"]:
        os.execvp("sherlock", "sherlock -c /bakerst.conf".split())
    else:
        assert args["watson"], args
        os.execvp("watson", "watson -c /bakerst.conf".split())


if __name__ == "__main__":
    exit(main(docopt(__doc__)))