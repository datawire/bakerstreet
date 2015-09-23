[Datawire]
directory_host = ${directory_host}

[Watson]
; The name of the service. This must be unique within the Datawire directory. The name must also satisfy the following
; constraints.
;
; Constraints
; -----------
; length: 1..100 characters
; case: lower-case only
; allowed characters: alphanumeric, underscore and hyphen.
; misc: must start with a letter or underscore

service_name: foo

; The service health check URL. The URL must respond to HTTP GET requests.
;
; Warning: Be careful using property reference syntax to blindly populate service_url here (e.g. %(service_url)s because
;          defining an additional path will cause problems. For example, if service_url is http://localhost:9000/foo and
;          you use $(service_url)/health then Watson will health check http://localhost:9000/foo/health which is most
;          likely what you do not want to do.
;
; Examples: http://localhost:9000/health

health_check_url: http://localhost:5001/health

; The number of seconds between health checks.

period: 3

; logging level (default in datawire.conf). Valid options are: DEBUG, INFO, WARNING, ERROR, or CRITICAL.

logging: DEBUG

; The hostname (or IP address) and port number of the service. Optionally a path may be specified by appending it after
; the host portion of the URI.
;
; Examples: http://localhost:9000 or http://localhost:9000/foobar