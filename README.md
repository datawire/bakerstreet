#Baker Street

Baker Street is a service discovery and routing system designed for microservice architectures. 

Baker Street simplifies scaling, testing, and upgrading microservices by:

* focusing on high availability and eventual consistency of the overall system
* enabling canary testing for staged testing and deployment of service upgrades
* supporting language, framework, and tooling independence for developers

Baker Street consists of three components:

* Sherlock - a routing system with local instances corresponding to each instance of your application to determine where connections from that instance should go
* Watson - a health checker with local instances corresponding to each instance of your application
* Datawire Directory - a global registration service recording server availability that receives availability information from each Watson instance and pushes changes in availability to local Sherlock instances as needed.

##Baker Street System Requirements

You must have the following on every system containing a Baker Street component:

1. Any Enterprise Linux 7 or Ubuntu 14.04 LTS
2. JDK 1.8
3. Maven 3 or higher

##Installing Baker Street

We expect it to take approximately 15 minutes to install a working local development environment with all three components.

Directions for installing Baker Street locally can be found [http://bakerstreet.io/docs/quickstart.html#setup][here].

##Next Steps

Additional information about Baker Street's design and architecture can be found [http://bakerstreet.io/docs/architecture.html][here].

Baker Street components all support a variety of options available via configuration files. For example, each component supports a range of logging levels from DEBUG (the most verbose) to CRITICAL (only logging errors that cause crashes) that can be independently toggled within these configuration files. Information on how to configure each component can be found [http://bakerstreet.io/docs/reference.html][here].

##Additional Information

For additional information, visit the Baker Street website at [http://www.bakerstreet.io].

Please post any questions about Baker Street on [http://www.stackoverflow.com][Stack Overflow] using the tag bakerstreet.
