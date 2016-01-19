/*
 * Copyright 2015, 2016 Datawire. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use self file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * The official Datawire Connect implementation for Datawire Hub.
 */

@version("1.0.0")
package hub {

  @doc("Contains Hub domain model interfaces and classes.")
  package model {
    @doc("Interface for health checks")
    interface HealthCheck {
      bool check();
    }

    interface ToJSON {
      JSONObject toJSON();
    }

    class ServiceEndpoint extends ToJSON {

      String name;
      String path;
      String address;
      int port;
      String scheme;

      ServiceEndpoint(String name, String scheme, String address, int port, String path) {
        self.name = name;
        self.scheme = scheme;
        self.address = address;
        self.port = port;
        self.path = path;
      }

      String toString() {
        return scheme + "://" + address + ":" + port.toString() + path;
      }

      JSONObject toJSON() {
        JSONObject json = new JSONObject();
        json["name"] = name;
        json["scheme"] = scheme;
        json["address"] = address;
        json["port"] = port;
        json["path"] = path;
        return json;
      }
    }
  }

  package message {

    @doc("The base message type")
    class HubMessage {

      @doc("ID of the message; Not used currently")
      int id = 0;

      @doc("The message type")
      String type = "";

      @doc("The time the message was created")
      long timestamp = 0;

      HubMessage(String type) {
        self.type = type;
        self.timestamp = now();
      }

      void dispatch(client.HubHandler handler) {
        handler.onHubMessage(self);
      }

      JSONObject toJSON() {
        JSONObject json = new JSONObject();
        json["type"] = self.type;
        json["time"] = self.timestamp;
        return json;
      }

      String toString() {
        return "HubMessage(id=" + id.toString() + ", type=" + type + ", timestamp=" + timestamp.toString() + ")";
      }
    }

    @doc("A message indicating a service endpoint should be added. ")
    class AddService extends HubMessage {

      model.ServiceEndpoint endpoint;

      AddService(model.ServiceEndpoint endpoint) {
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

      void dispatch(client.HubHandler handler) {
          handler.onHubMessage(self);
      }
    }

    @doc("A message indicate a service endpoint should be removed.")
    class RemoveService extends HubMessage {

      model.ServiceEndpoint endpoint;

      RemoveService(model.ServiceEndpoint endpoint) {
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

      void dispatch(client.HubHandler handler) {
          handler.onHubMessage(self);
      }
    }

    @doc("A message indicating a client would like the latest state from the server.")
    class Synchronize extends HubMessage {

      String data;

      Synchronize(JSONObject json) {
          super("synchronize");
          data = json.toString();
      }

      void dispatch(client.HubHandler handler) {
          handler.onSynchronize(self);
      }
    }

    @doc("A message indicating a service is still alive and well.")
    class Heartbeat extends HubMessage {

      Heartbeat() {
          super("heartbeat");
      }

      void dispatch(client.HubHandler handler) {
          handler.onHeartbeat(self);
      }
    }

    @doc("A message indicating a client is interested in subscribing to the services registry.")
    class Subscribe extends HubMessage {
      Subscribe() {
          super("subscribe");
      }

      void dispatch(client.HubHandler handler) {
          handler.onSubscribe(self);
      }
    }

    @doc("A message indicating the client has connected")
      class Connected extends HubMessage {
        Connected() {
          super("connected");
        }

        void dispatch(client.HubHandler handler) {
          handler.onConnected(self);
        }
      }

      @doc("A message indicating the client has disconnected")
      class Disconnected extends HubMessage {
      Disconnected() {
        super("disconnected");
      }

      void dispatch(client.HubHandler handler) {
        handler.onDisconnected(self);
      }
    }

    @doc("A message indicating the server or client experienced an error")
    class HubError extends HubMessage {

      @doc("A unique authoritative code for the error")
      int code;

      @doc("A short string that identifies the code. Preference should be given to the code number instead of the name")
      String  codeName;

      HubError(int code, String codeName) {
        super("hub-error");
        self.code = code;
        self.codeName = codeName;
      }
    }

    interface MessageFactory {
      message.HubMessage build(String type, JSONObject json);
    }

    class DefaultMessageFactory extends MessageFactory {
      message.HubMessage build(String type, JSONObject json) {
        if (type == "connected")    { return new message.Connected(); }
        if (type == "disconnected") { return new message.Disconnected(); }
        if (type == "sync")         { return new message.Synchronize(json); }

        return new message.HubMessage(type);
      }
    }
  }

  @doc("Contains Hub client interfaces and classes")
  package client {

    @doc("Default handler implementation for Datawire Hub messages")
    class DefaultHubHandler extends HubHandler { }

    @doc("Basic Hub client that must be extended to provide features beyond connecting to the Hub")
    class HubClient extends HTTPHandler, HubHandler, Task, WSHandler {

      @doc("Datawire Connect Runtime")
      Runtime runtime;

      @doc("WebSocket connection")
      WebSocket socket;

      @doc("Hub Gateway Configuration")
      GatewayOptions gateway;

      @doc("The URL of the Datawire Hub")
      String hubUrl;

      HubClient(Runtime runtime, GatewayOptions gateway) {
        self.runtime = runtime;
        self.gateway = gateway;
      }

      void connect() {
        if (socket == null) {
          HTTPRequest request = new HTTPRequest(gateway.buildUrl());
          request.setMethod("POST");
          request.setHeader("Authorization", "Bearer " + gateway.getToken());
          runtime.request(request, self);
        }
      }

      void disconnect() {
        if (socket != null) {
          socket.close();
        }
      }

      @doc("The task to run")
      void onExecute(Runtime runtime);

      bool isConnected() {
        return socket != null;
      }

      @doc("Schedules the task for execution after the specified period")
      void schedule(float period) {
        runtime.schedule(self, period);
      }

      @doc("Schedules the task for execution immediately")
      void scheduleNow() {
        runtime.schedule(self, 0.0);
      }

      void send(String payload) {
        if (socket != null && isConnected()) {
          socket.send(payload);
        }
      }

      void sendMessage(message.HubMessage message) {
        if (message != null) {
          JSONObject json = message.toJSON();
          send(json.toString());
        }
      }

      void onHTTPResponse(HTTPRequest request, HTTPResponse response) {
        if (response.getCode() == 200) {
          JSONObject connectionInfo = response.getBody().parseJSON();
          hubUrl = connectionInfo["url"];
          print(hubUrl + "v1/registry?token=" + gateway.getToken());
          runtime.open(hubUrl + "v1/registry?token=" + gateway.getToken(), self);
        } else {
          message.HubError error = new message.HubError(response.getCode(), "http-error");
          error.dispatch(self);
        }
      }

      void onWSError(WebSocket socket) {
        message.HubMessage msg = self.buildMessageOfType("disconnected", new JSONObject());
        msg.dispatch(self);
      }

      void onWSConnected(WebSocket socket) {
        self.socket = socket;
        message.HubMessage msg = self.buildMessageOfType("connected", new JSONObject());
        msg.dispatch(self);
      }

      void onWSClosed(WebSocket socket) {
        socket = null;
        message.HubMessage msg = self.buildMessageOfType("disconnected", new JSONObject());
        msg.dispatch(self);
      }

      void onWSMessage(WebSocket socket, String message) {
        JSONObject json = message.parseJSON();
        String type = json["type"].getString();
        message.HubMessage msg = self.buildMessageOfType(type, json);
        msg.dispatch(self);
      }

      message.HubMessage buildMessageOfType(String type, JSONObject json) {
        if (type == "connected")    { return new message.Connected(); }
        if (type == "disconnected") { return new message.Disconnected(); }
        if (type == "sync")         { return new message.Synchronize(json); }

        return new message.HubMessage("message");
      }

      message.HubMessage buildMessage(JSONObject json) {
        String type = json["type"].getString();
        return buildMessageOfType(type, json);
      }
    }

    @doc("Handler for Datawire Hub messages")
    interface HubHandler {
      void onClientError(message.HubError error) {
        self.onHubMessage(error);
      }

      void onConnected(message.Connected connect) {
        self.onHubMessage(connect);
      }

      void onDisconnected(message.Disconnected disconnected) {
        self.onHubMessage(disconnected);
      }

      void onError(message.HubError error) {
        if (error.code > 999 && error.code < 2000)  { self.onServerError(error); }
        if (error.code > 1999 && error.code < 3000) { self.onClientError(error); }
      }

      void onHeartbeat(message.Heartbeat heartbeat) {
        self.onHubMessage(heartbeat);
      }

      void onHubMessage(message.HubMessage message) {
        // generic do-nothing handler
      }

      void onServerError(message.HubError error) {
        self.onHubMessage(error);
      }

      void onSubscribe(message.Subscribe sub) {
        self.onHubMessage(sub);
      }

      void onSynchronize(message.Synchronize sync) {
        self.onHubMessage(sync);
      }
    }

    class GatewayOptions {
      bool    secure = true;
      bool    authenticate = true;

      String  gatewayHost = "hub-gw.datawire.io";
      int     gatewayPort = 443;
      String  gatewayConnectorPath = "/v1/connect";

      String  token = "";

      GatewayOptions(String token) {
        self.token = token;
      }

      String getToken() {
        return token;
      }

      String buildUrl() {
        String scheme = "https";
        int gatewayPort = self.gatewayPort;

        if (secure) {
          if (gatewayPort == null || gatewayPort < 1 || gatewayPort > 65535) {
            gatewayPort = 443;
          }
        } else {
          scheme = "http";
          if (gatewayPort == null || gatewayPort < 1 || gatewayPort > 65535) {
            gatewayPort = 80;
          }
        }

        return scheme + "://" + gatewayHost + ":" + gatewayPort.toString() + gatewayConnectorPath;
      }
    }
  }
}