.. _architecture:

Design and Architecture
=======================

Baker is patterned after `AirBnb's SmartStack
<http://nerds.airbnb.com/smartstack-service-discovery-cloud/>`_ which
is an excellent piece of software and design. The aforereferenced
blog post gives a terrific overview of the different approaches to
service discovery and routing, which we generally agree with (hence,
our adoption of the overall approach).

Baker does make several different design decisions than SmartStack.

#. Baker isolates its use of HAProxy from the user. We did this
   because HAProxy is commonly deployed in architectures where it is
   both a bottleneck and a single point of failure and that usage
   significantly influences its design and engineering with respect to
   robustness and performance.

   In this architecture HAProxy is paired with each service client and
   therefore neither a single point of failure nor a bottleneck. While
   HAProxy is an excellent conservative choice to start with, we
   expect it may ultimately make sense to replace HAProxy with a
   component that makes a different set of tradeoffs that better fit
   its role.

   For example HAProxy supports HTTP and TCP, but does not natively
   support other protocols. In particular, HAProxy does not support
   any async messaging protocols, which are important for many use
   cases in microservices. Also, HAProxy's load balancing algorithms
   tend to assume that it is the only thing dispatching load to a
   given backend, however that is not the case in this architecture.

#. Baker uses the Datawire directory service instead of Zookeeper.
   Zookeeper provides a strongly consistent model; the directory
   service focuses on availability. This also simplifies Baker
   deployment.

Deployment Model
----------------

A Baker deployment involves three different types of nodes. A
directory node, a service node, and a client node. Although a node can
take on all three roles and in practice many nodes will be both
service and client nodes, it is conceptually easier to consider the
three distinct node types individually.

Directory Node
~~~~~~~~~~~~~~

The Directory node functions as a rendezvous point between services and
clients. Each service node broadcasts its presence and location to the
directory, and the directory notifies any interested client nodes as
service nodes come and go.

There is exactly one Directory node per Baker deployment. Every
service and client must be configured with the location of this node.
We expect to support multiple Directory nodes in future versions of
Baker.

Service Nodes
~~~~~~~~~~~~~

A service node is responsible for keeping the directory accurately
informed of its presence and location. Baker relies on the ``watson``
process to check the health of the service and communicate its
presence and location to the directory. ``watson`` should always be
deployed on the same server/container as the service it is
monitoring. This deployment model minimizes issues related to node
failure or network partitions, since ``watson`` can monitor the host
service directly over localhost.

Client Nodes
~~~~~~~~~~~~

A client node maintains a table of the location of all relevant
service nodes and updates this whenever the directory notifies the
client of changes in the state of services. Baker relies on the
``sherlock`` process to gather information from the directory about
all available services and dynamically proxy connections from its
co-located client processes accordingly. ``sherlock`` should always be
deployed on the same server/container as the client processes it is
supporting.

Discovery Protocol
------------------

Service Nodes
~~~~~~~~~~~~~

A service node contains the following state:

* The address of the directory.
* The virtual address of the service.
* The physical address of the service.
* A heartbeat interval.

A service node is responsible for initiating contact with the
directory and informing the directory of its presence at least once
per heartbeat interval. If the directory node is unavailable for any
reason, the service node will continue to retry indefinitely.

Client Nodes
~~~~~~~~~~~~

A client node contains the following state:

* The address of the directory.
* An initially empty table of routes mapping virtual to physical
  addresses.

A client node is responsible for initiating contact with the directory
and registering its interest in receiving updates. If the directory
node is unavailable for any reason, the client node will continue to
retry indefinitely.

Directory Node
~~~~~~~~~~~~~~

The directory node contains the following state:

* An initially empty table of routes mapping virtual to physical
  addresses.
* An initially empty list of client nodes interested in receiving
  updates.

The directory node is responsible for adding, updating, and removing
entries to/from the table of routes based on the presence/absence of
heartbeats from service nodes. The directory will also update
interested clients when an entry is added, updated, or removed. When a
client initially registers interest in receiving updates, the new
client will be caught up by receiving the full table of routes prior
to being informed of any subsequent updates.

Startup Order and Node Failures
-------------------------------

Several key properties of the discovery protocol allow it to be
resilient to both arbitrary startup order and node failures.

#. The service and client nodes are guaranteed to retry if the
   directory node is not currently available.

#. The directory contains no state that is not dynamically constructed
   from the set of active service and client nodes.

#. The directory catches up client nodes as they join.

#. The client nodes replicate the routes published by the directory.

Given the above, any configuration of nodes is guaranteed to reach the
same (or equivalent) end state regardless of startup order.
Additionally, given the final property, even if the directory node
fails, all existing service and client nodes will continue to function
normally. The only impact on the overall system will be the inability
to dynamically add new service or client nodes.

These properties make for an extremely resilient design even with a
single directory node. Given that adding and removing service and
client nodes is not a high volume operation, a deployment can easily
tolerate temporary failures of the directory node, as well as short
periods of downtime if needed for maintenance.

Network Partitions
------------------

In the event of a network partition, all client nodes reachable from
the directory will be dynamically updated to use only reachable
service nodes. Client nodes that are not reachable from the directory
will continue to attempt to access all service nodes that were
available prior to the network partition.

Future Work
-----------

We expect to extend the system in a future release to support multiple
directory nodes. This will provide the following benefits:

#. Scalability and availability of directory services for deployments
   where adding and removing service and/or client nodes *is* expected
   to be a high volume operation.

#. The ability to provide better introspection for nodes that are not
   reachable from the directory in the event of a network partition.
