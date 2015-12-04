@version("1.0.0")
package hub {

    @doc("Datawire Hub Non-event/non-message domain model objects.")
    package model {
        @doc("Interface for health checks")
        interface HealthCheck {
            bool check();
        }

        @doc("Represents the IP or DNS name associated with a service endpoint")
        class NetworkAddress extends ToJSON {

          String host;
          String type;

          NetworkAddress(String host, String type) {
            self.host = host;
            self.type = type;
          }

          JSONObject toJSON() {
            JSONObject json = new JSONObject();
            json["host"] = host;
            json["type"] = type;
            return json;
          }

          String toString() {
            return host;
          }
        }

        @doc("Represents the port associated with a service endpoint and the protocol it handles")
        class ServicePort extends ToJSON {

          String name;
          int port;

          ServicePort(String name, int port) {
            self.name = name;
            self.port = port;
          }

          String toString() {
            return name + "-" + port.toString();
          }

          JSONObject toJSON() {
            JSONObject json = new JSONObject();
            json["name"] = name;
            json["port"] = port;
            json["secure"] = false;
            return json;
          }
        }

        @doc("Represents the combination of network address and service port.")
        class ServiceEndpoint extends ToJSON {

          String name;
          String path = null;
          NetworkAddress address;
          ServicePort port;

          ServiceEndpoint(String name, NetworkAddress address, ServicePort port) {
            self.name = name;
            self.address = address;
            self.port = port;
            self.path = "/";
          }

          String toString() {
            return port.name + "://" + address.host + ":" + port.port.toString();
          }

          JSONObject toJSON() {
            JSONObject json = new JSONObject();
            json["name"] = name;
            json["address"] = address.toJSON();
            json["port"] = port.toJSON();
            json["path"] = path;
            return json;
          }
        }

        @doc("Maps a named service to a set of known endpoints.")
        class ServiceRecord {

          String name;
          List<String> endpoints;

          ServiceRecord(String name) {
            self.name = name;
            self.endpoints = new List<String>();
          }

          String toString() {
            String result  = "";

            String header  = "Record: " + name;
            String pointer = " --> ";

            result = result + header;

            // build padding for pretty printing
            String padding = "";
            int pdx = 0;
            while(pdx < header.size()) {
              padding = padding + " ";
              pdx = pdx + 1;
            }

            // build the result
            int edx = 0;
            while(edx < endpoints.size()) {
              if (edx != 0) {
                result = result + padding;
              }

              result = result + pointer + endpoints[edx] + "\n";
              edx = edx + 1;
            }

            return result;
          }

          JSONObject toJson() {
            JSONObject json = new JSONObject();
            return json;
          }
        }
    }

    @doc("Messages that can be sent to the Datawire Hub.")
    package message {

        @doc("The message type")
        class RegistryMessage {

            @doc("ID of the message")
            int id = 0;

            @doc("The message type")
            String type = null;

            @doc("The time the message was created")
            long timestamp = now();

            RegistryMessage(String type) {
              self.type = type;
            }

            JSONObject toJSON() {
                JSONObject json = new JSONObject();
                json["id"] = self.id;
                json["type"] = self.type;
                json["time"] = self.timestamp;
                return json;
            }
        }

        @doc("A message indicating a service endpoint should be added. ")
        class AddServiceEndpoint extends RegistryMessage {

            model.ServiceEndpoint endpoint;

            AddServiceEndpoint(model.ServiceEndpoint endpoint) {
                super("add-service");
                self.endpoint = endpoint;
            }

            JSONObject toJSON() {
                JSONObject json = super.toJSON();

                print(json.toString());

                if (endpoint != null) {
                    json["endpoint"] = endpoint.toJSON();
                } else {
                    json["endpoint"] = null;
                }

                return json;
            }
        }

        @doc("A message indicate a service endpoint should be removed.")
        class RemoveServiceEndpoint extends RegistryMessage {

            model.ServiceEndpoint endpoint;

            RemoveServiceEndpoint(model.ServiceEndpoint endpoint) {
                super("remove-service");
                self.endpoint = endpoint;
            }

            JSONObject toJSON() {
                JSONObject json = super.toJSON();

                if (endpoint != null) {
                    json["endpoint"] = endpoint.toJSON();
                } else {
                    json["endpoint"] = null;
                }

                return json;
            }
        }

        @doc("A message indicating a service is still alive and well.")
        class Heartbeat extends RegistryMessage {

            Heartbeat() {
                super("heartbeat");
            }
        }
    }

    @doc("Events that can be received by Datawire Hub clients.")
    package event {
        @doc("Base class for all Datawire Hub service registry events.")
        class RegistryEvent {

            @doc("The event type")
            String type;

            @doc("The timestamp associated with the event")
            String timestamp = null;

            RegistryEvent(String type) {
                self.type = type;
            }

            void dispatch(RegistryHandler handler) {
                handler.onRegistryEvent(self);
            }
        }

        @doc("Represents an update to the service registry")
        class RegistryUpdate extends RegistryEvent {

            List<model.ServiceRecord> records = [];

            RegistryUpdate(String type, JSONObject json) {
                super(type);
            }

            void dispatch(RegistryHandler handler) {
                handler.onRegistryUpdate(self);
            }
        }

        class RegistryJoin extends RegistryEvent {

            RegistryJoin(String type, JSONObject json) {
                super(type);
            }

            void dispatch(RegistryHandler handler) {
                handler.onRegistryJoin(self);
            }
        }

        @doc("Indicates a service endpoint has left or been removed from the registry")
        class RegistryLeave extends RegistryEvent {

            @doc("The name of the service")
            String service;

            @doc("The ID of endpoint being removed (format: <scheme>://<network-address>:<port>)")
            String id;

            RegistryLeave(String type, JSONObject json) {
                super(type);
                self.service = json[""];
                self.id = json[""];
            }

            void dispatch(RegistryHandler handler) {
                handler.onRegistryLeave(self);
            }
        }
    }

    @doc("Datawire Hub service registry subscription")
    class RegistrySubscription extends WSHandler {

        Runtime         runtime;
        WebSocket       socket = null;
        RegistryHandler handler = null;

        RegistrySubscription(Runtime runtime, RegistryHandler handler) {
           self.runtime = runtime;
           self.handler = handler;
        }

        void connect(String host, int port) {
            String address = "ws://" + host + ":" + port.toString() + "/v1/services";
            self.runtime.open(address, self);
        }

        void disconnect() {
            socket.close();
        }

        void subscribe(String host, int port) {
            String address = "ws://" + host + ":" + port.toString() + "/v1/services";
            self.runtime.open(address, self);
        }

        void unsubscribe() {
            socket.close();
        }

        void send(String message) {
            if (socket != null) {
                socket.send(message);
            } else {
                // todo: error event?
            }
        }

        void onWSConnected(WebSocket socket) {
            self.socket = socket;
            event.RegistryEvent event = self.buildEvent("join", new JSONObject());
            event.dispatch(handler);
        }

        void onWSClosed(WebSocket socket) {
            self.socket = null;
            event.RegistryEvent event = self.buildEvent("leave", new JSONObject());
            event.dispatch(handler);
        }

        void onWSMessage(WebSocket socket, String message) {
            JSONObject json = message.parseJSON();
            String type = json["type"].getString();
            event.RegistryEvent event = self.buildEvent(type, json);
            event.dispatch(handler);
        }

        event.RegistryEvent buildEvent(String type, JSONObject json) {
            if (type == "join")     { return new event.RegistryJoin(type, json); }
            if (type == "leave")    { return new event.RegistryLeave(type, json); }
            return new event.RegistryEvent("event");
        }
    }

    interface ToJSON {
        JSONObject toJSON();
    }

    @doc("Handler for Datawire Hub service registry events")
    interface RegistryHandler {
        void onRegistryEvent(event.RegistryEvent event) {
            // generic do-nothing handler
        }

        void onRegistryUpdate(event.RegistryUpdate update) {
            self.onRegistryEvent(update);
        }

        void onRegistryJoin(event.RegistryJoin connect) {
            self.onRegistryEvent(connect);
        }

        void onRegistryLeave(event.RegistryLeave leave) {
            self.onRegistryEvent(leave);
        }
    }

    @doc("Default handler implementation for Datawire Hub service registry events")
    class DefaultRegistryHandler extends RegistryHandler { }

    @doc("Base implementation of a Datawire Hub service registry client")
    class RegistryClient extends Task {

        Runtime                 runtime;
        String                  hubHost;
        int                     hubPort;
        RegistrySubscription    connection = null;

        RegistryClient(Runtime runtime, String hubHost, int hubPort) {
            self.runtime = runtime;
            self.hubHost = hubHost;
            self.hubPort = hubPort;
        }

        bool isConnected() {
            if (connection != null) {
                return connection.socket != null;
            }

            return false;
        }

        void send(String data) {
            if (connection != null) {
                connection.send(data);
            }
        }

        void disconnect() {
            if (connection != null) {
                connection.unsubscribe();
            }
        }

        void subscribe(RegistryHandler handler) {
            connection = new RegistrySubscription(runtime, handler);
            connection.subscribe(hubHost, hubPort);
        }

        void onExecute(Runtime runtime) { }
    }
}