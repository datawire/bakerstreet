# Change Log
All notable modifications to the Baker Street project (bakerstreet.io) will be documented in this file.

## [0.6] - 2015-12-??

### Changed
- Single package "datawire-bakerstreet"
- New YAML configuration format
- Uses the [Datawire Hub](https://github.com/datawire/hub) instead of Apache Qpid Proton
- More advanced health check configuration

### Added
- Added the hudson program which provides a very simple little REST service for smoke and sanity testing

## [0.5] - 2015-09-25
### Changed
- Renamed "liveness_url" to "health_check_url" in Watson config file.
- Improved Watson and Sherlock config file comments.

### Added
- Added a new Watson configuration property "service_name" that replaces setting a service_name in Watson's service URL. This allows Baker Street to route traffic to microservices that are exposed on a specific URL path. (issue: datawire/bakerstreet#4)