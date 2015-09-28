.. _reference:

Reference
=========

The Datawire Baker components rely on configuration files to manage setup. The individual components look in ``/etc/datawire`` and ``~/.datawire`` for standard files, with the contents of the latter overriding the contents of the former. The ``--config`` command line option allows an additional file to be specified, with its contents overriding the prior files.

Every component starts by loading ``datawire.conf``::

  [DEFAULT]
  ; logging level may be DEBUG, INFO, WARNING, ERROR, or CRITICAL
  logging: WARNING

  [Datawire]
  ; Change this to the well known and stable hostname of the directory for your deployment.
  directory_host: localhost

This configuration file allows the specification of the default logging level for every Datawire component, but individual component configurations may override this by specifying a different ``logging`` directive. Component log output goes to stdout, with the operating system's service control mechanism (systemd, Upstart, etc.) handling output redirection (to the system journal, to ``/var/log/upstart/*.log``, etc.).

This configuration file also contains the central designation for the host running the Datawire Directory. As one directory can serve an entire site installation, it is convenient to have this hostname specified in one place.

Directory
---------

A single Datawire Directory allows all other Baker components to communicate. Unlike the other components, the directory allows significant configuration by command line options.

At the command line::

  usage: directory [-h] [-c FILE] [-n HOST] [-p PORT] [-a ADDRESS] [-l LEVEL]
                   [-V]

  optional arguments:
    -h, --help            show this help message and exit
    -c FILE, --config FILE
                          read from additional config file
    -n HOST, --host HOST  network host (defaults to localhost)
    -p PORT, --port PORT  network port (defaults to 5672)
    -a ADDRESS, --address ADDRESS
                          amqp address, defaults to //<host>[:<port]
    -l LEVEL, --level LEVEL
                          logging level
    -V, --version         show program's version number and exit

The command line ``host`` option must be set to an externally-visible hostname for the machine running the directory; it is typically pulled from the ``directory_host`` field in ``datawire.conf`` as described above. The ``port`` and ``address`` command line options are for unusual deployments only.

By config file::

  [Directory]
  ; logging level (default in datawire.conf) may be DEBUG, INFO, WARNING, ERROR, or CRITICAL
  ;logging: WARNING

The configuration file has just one commented-out option for changing the directory's logging level from the default.

Sherlock
--------

A client node, which is to say a server, VM, or container that runs software that needs to access services, runs Sherlock to enable said access. Sherlock is typically deployed using its configuration file ``/etc/datawire/sherlock.conf`` and system service integration, but the command line allows specifying an additional configuration file to support special case usage.

At the command line::

  usage: sherlock [-h] [-c FILE]

  optional arguments:
    -h, --help            show this help message and exit
    -c FILE, --config FILE
                          read from additional config file

The standard config file lists all the fields::

  [Sherlock]
  ; The path to the HAProxy executable
  proxy: /usr/sbin/haproxy

  ; The directory where HAProxy runs from and reads its configuration.
  rundir: /opt/datawire/run

  ; The debounce period in seconds. The debounce period is designed to prevent HAProxy from constantly restarting
  ; because of changes.
  debounce: 2
  dir_debounce: 2

  ; logging level (default in datawire.conf). Valid options are: DEBUG, INFO, WARNING, ERROR, or CRITICAL.
  ;logging: WARNING

Sherlock gathers information about running services and the URLs of the microservices that implement them from the directory (as specified in ``datawire.conf``). It configures and launches HAProxy (as specified by the ``proxy`` parameter), keeping HAProxy-specific files in the path specified by the ``rundir`` parameter.

Reconfiguring HAProxy can introduce a brief interruption of service (well under a second), so Sherlock coalesces updates from the directory. When there are no new updates for two seconds (as configured by the ``debounce`` parameter in seconds), Sherlock outputs a new HAProxy configuration and reconfigures HAProxy. If Sherlock detects that it has disconnected from and then reconnected to the directory, it instead coaslesces over ``dir_debounce`` seconds.

The configuration file has a commented-out option for changing sherlock's logging level from the default.

Watson
------

In a typical deployment, one microservice is deployed per server, VM, or container. Watson is deployed alongside that microservice using its configuration file ``/etc/datawire/watson.conf`` and system service integration. The command line ``--config`` option exists to enable launching multiple instances of Watson on a single machine by specifying alternate configuration files.

At the command line::

  usage: watson [-h] [-c FILE]

  optional arguments:
    -h, --help            show this help message and exit
    -c FILE, --config FILE
                          read from additional config file

The config file prototype ``watson.conf.proto`` lists all fields::

  [Watson]
  ; The hostname (or IP address) and port number of the service. Optionally a path may be specified by appending it after
  ; the host portion of the URI.
  ;
  ; Examples: http://localhost:9000 or http://localhost:9000/foo

  service_url: http://hostname:port

  ; The name of the service. This must be unique within the Datawire directory. The name must also satisfy the following
  ; constraints.
  ;
  ; Constraints
  ; -----------
  ; length: 1..100 characters
  ; case: lower-case only
  ; allowed characters: alphanumeric, underscore and hyphen.
  ; misc: must start with a letter or underscore

  service_name: foobar

  ; The service health check URL. The URL must respond to HTTP GET requests.
  ;
  ; Warning: Be careful using property reference syntax to blindly populate service_url here (e.g. %(service_url)s because
  ;          defining an additional path will cause problems. For example, if service_url is http://localhost:9000/foo and
  ;          you use $(service_url)/health then Watson will health check http://localhost:9000/foo/health which is most
  ;          likely what you do not want to do.
  ;
  ; Examples: http://localhost:9000/health

  health_check_url: http://hostname:port/health

  ; The number of seconds between health checks.

  period: 3

  ; logging level (default in datawire.conf). Valid options are: DEBUG, INFO, WARNING, ERROR, or CRITICAL.

  ;logging: WARNING

The path portion of the ``service_url`` field ("service_name" in the prototype above) is used to identify a service. This *service name* serves two key purposes:

# Sherlock uses the *service name* portion of incoming requests to determine where to route/proxy the request.
# Every microservice whose associated *service name* is set to a particular name (e.g., greeting) is considered equivalent for load balancing.

Watson connects to the liveness check URL every three seconds (as configured by the ``period`` parameter). If the service appears live (returns an HTTP response of 200), Watson ensures that the directory (as specified in ``datawire.conf``) is aware that the service is being served at the specified ``service_url``.

The configuration file has a commented-out option for changing watson's logging level from the default.
