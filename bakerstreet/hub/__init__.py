from quark_runtime import *

import model
import message
import event


class RegistrySubscription(object):
    """
    Datawire Hub service registry subscription
    """
    def _init(self):
        self.runtime = None
        self.socket = None
        self.handler = None

    def __init__(self, runtime, handler):
        self._init()
        (self).runtime = runtime
        (self).handler = handler

    def connect(self, host, port):
        address = ((((u"ws://") + (host)) + (u":")) + (str(port))) + (u"/v1/services");
        ((self).runtime).open(address, self);

    def disconnect(self):
        (self.socket).close();

    def subscribe(self, host, port):
        address = ((((u"ws://") + (host)) + (u":")) + (str(port))) + (u"/v1/services");
        ((self).runtime).open(address, self);

    def unsubscribe(self):
        (self.socket).close();

    def send(self, message):
        if ((self.socket) != (None)):
            (self.socket).send(message);
        else:
            pass

    def onWSConnected(self, socket):
        (self).socket = socket
        event = (self).buildEvent(u"join", _JSONObject());
        (event).dispatch(self.handler);

    def onWSClosed(self, socket):
        (self).socket = None
        event = (self).buildEvent(u"leave", _JSONObject());
        (event).dispatch(self.handler);

    def onWSMessage(self, socket, message):
        json = _JSONObject.parse(message);
        type = ((json).getObjectItem(u"type")).getString();
        event = (self).buildEvent(type, json);
        (event).dispatch(self.handler);

    def buildEvent(self, type, json):
        if ((type) == (u"join")):
            return event.RegistryJoin(type, json)

        if ((type) == (u"leave")):
            return event.RegistryLeave(type, json)

        return event.RegistryEvent(u"event")

    def onWSInit(self, socket):
        pass

    def onWSBinary(self, socket, message):
        pass

    def onWSError(self, socket):
        pass

    def onWSFinal(self, socket):
        pass

class ToJSON(object):

    def toJSON(self): assert False

class RegistryHandler(object):
    """
    Handler for Datawire Hub service registry events
    """

    def onRegistryEvent(self, event):
        pass

    def onRegistryUpdate(self, update):
        (self).onRegistryEvent(update);

    def onRegistryJoin(self, connect):
        (self).onRegistryEvent(connect);

    def onRegistryLeave(self, leave):
        (self).onRegistryEvent(leave);


class DefaultRegistryHandler(object):
    """
    Default handler implementation for Datawire Hub service registry events
    """
    def _init(self):
        pass
    def __init__(self): self._init()

    def onRegistryEvent(self, event):
        pass

    def onRegistryUpdate(self, update):
        (self).onRegistryEvent(update);

    def onRegistryJoin(self, connect):
        (self).onRegistryEvent(connect);

    def onRegistryLeave(self, leave):
        (self).onRegistryEvent(leave);


class RegistryClient(object):
    """
    Base implementation of a Datawire Hub service registry client
    """
    def _init(self):
        self.runtime = None
        self.hubHost = None
        self.hubPort = None
        self.connection = None

    def __init__(self, runtime, hubHost, hubPort):
        self._init()
        (self).runtime = runtime
        (self).hubHost = hubHost
        (self).hubPort = hubPort

    def isConnected(self):
        if ((self.connection) != (None)):
            return ((self.connection).socket) != (None)

        return False

    def send(self, data):
        if ((self.connection) != (None)):
            (self.connection).send(data);

    def disconnect(self):
        if ((self.connection) != (None)):
            (self.connection).unsubscribe();

    def subscribe(self, handler):
        self.connection = RegistrySubscription(self.runtime, handler)
        (self.connection).subscribe(self.hubHost, self.hubPort);

    def onExecute(self, runtime):
        pass
