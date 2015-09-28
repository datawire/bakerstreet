
def _getvar(var, path, default=None):
    with open(path) as f:
        for line in f:
            if var in line and "=" in line and "__all__" not in line:
                g = {}
                l = {}
                exec line in g, l
                return l[var]
    return default

def _version():
    import os
    return _getvar("__version__", os.path.join(os.path.dirname(__file__),
                                               "../../_metadata_watson.py"),
                   "X.X")

def _repo():
    return "stable"

version = _version()
repo = _repo()
install = "https://packagecloud.io/datawire/%s/install" % repo
script_rpm = "https://packagecloud.io/install/repositories/datawire/%s/script.rpm.sh" % repo
script_deb = "https://packagecloud.io/install/repositories/datawire/%s/script.deb.sh" % repo
