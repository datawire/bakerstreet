# Baker Street

Baker Street is a service discovery and routing system designed for microservice architectures.

Baker Street simplifies scaling, testing, and upgrading microservices by:

* automatically splitting traffic among all healthy services sharing the same name in the system
* making load balancing more efficient and robust by using local load balancers
* removing problematic instances from the rotation more quickly by using local health checkers
* enabling canary testing for staged testing and deployment of service upgrades

Baker Street consists of three components:

* Sherlock - an HAProxy-based routing system with local instances corresponding to each instance of your application to determine where connections from that instance should go
* Watson - a health checker with local instances corresponding to each instance of your application
* Datawire Directory - a global service discovery mechanism that receives availability information from each Watson instance and pushes changes in availability to local Sherlock instances as needed

## Baker Street System Requirements

Baker Street works on any flavor of Enterprise Linux 7 or on Ubuntu 14.04 LTS. Since Baker Street must be co-located with your service, your service must also run on one of these platforms if you wish to use it with Baker Street. Baker Street has no other requirements; you are free to use the language, framework, and tools of your choice while integrating with it.

That said, if you wish to test your installation using a simple sample service as outlined in the Baker Street documentation, you will also need the following:

* JDK 1.8
* maven 3 or higher

## Installing Baker Street

We expect it to take approximately 15 minutes to install a working local development environment with all three components.

Directions for installing Baker Street locally can be found [here](http://bakerstreet.io/docs/quickstart.html#setup).

## Next Steps

Additional information about Baker Street's design and architecture can be found [here](http://bakerstreet.io/docs/architecture.html).

Baker Street components all support a variety of options available via configuration files. For example, each component supports a range of logging levels that can be independently toggled within these configuration files. Information on how to configure each component can be found [here](http://bakerstreet.io/docs/reference.html).

## Additional Information

For additional information, visit the Baker Street website at [http://www.bakerstreet.io](http://www.bakerstreet.io).

Please post any questions about Baker Street on [Stack Overflow](http://www.stackoverflow.com) using the tag bakerstreet.
