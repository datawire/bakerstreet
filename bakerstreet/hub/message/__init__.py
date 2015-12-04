from quark_runtime import *

import hub.model


class RegistryMessage(object):
    """
    The message type
    """
    def _init(self):
        self.id = 0
        self.type = None
        self.timestamp = long(time.time()*1000)

    def __init__(self, type):
        self._init()
        (self).type = type

    def toJSON(self):
        json = _JSONObject();
        (json).setObjectItem((u"id"), ((_JSONObject()).setNumber((self).id)));
        (json).setObjectItem((u"type"), ((_JSONObject()).setString((self).type)));
        (json).setObjectItem((u"time"), ((_JSONObject()).setNumber((self).timestamp)));
        return json


class AddServiceEndpoint(RegistryMessage):
    """
    A message indicating a service endpoint should be added.
    """
    def _init(self):
        RegistryMessage._init(self)
        self.endpoint = None

    def __init__(self, endpoint):
        super(AddServiceEndpoint, self).__init__(u"add-service");
        (self).endpoint = endpoint

    def toJSON(self):
        json = super(AddServiceEndpoint, self).toJSON();
        _println((json).toString());
        if ((self.endpoint) != (None)):
            (json).setObjectItem((u"endpoint"), ((self.endpoint).toJSON()));
        else:
            (json).setObjectItem((u"endpoint"), (None));

        return json


class RemoveServiceEndpoint(RegistryMessage):
    """
    A message indicate a service endpoint should be removed.
    """
    def _init(self):
        RegistryMessage._init(self)
        self.endpoint = None

    def __init__(self, endpoint):
        super(RemoveServiceEndpoint, self).__init__(u"remove-service");
        (self).endpoint = endpoint

    def toJSON(self):
        json = super(RemoveServiceEndpoint, self).toJSON();
        if ((self.endpoint) != (None)):
            (json).setObjectItem((u"endpoint"), ((self.endpoint).toJSON()));
        else:
            (json).setObjectItem((u"endpoint"), (None));

        return json


class Heartbeat(RegistryMessage):
    """
    A message indicating a service is still alive and well.
    """
    def _init(self):
        RegistryMessage._init(self)

    def __init__(self):
        super(Heartbeat, self).__init__(u"heartbeat");


class Subscribe(RegistryMessage):
    """
    A message indicating a client is interested in subscribing to the services registry.
    """
    def _init(self):
        RegistryMessage._init(self)

    def __init__(self):
        super(Subscribe, self).__init__(u"subscribe");

