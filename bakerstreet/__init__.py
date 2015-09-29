import logging
import logging.config
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

DEFAULT_WATSON_CONFIG = """
[DEFAULT]
logging: WARNING

[Datawire]
directory_host:

[Watson]
period: 3
"""

DEFAULT_SHERLOCK_CONFIG = """
[DEFAULT]
logging: WARNING

[Datawire]
directory_host:

[Sherlock]
proxy: /usr/sbin/haproxy
rundir: .
debounce: 2
dir_debounce: 2
"""