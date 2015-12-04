from quark_runtime import *

import hub


class HealthCheck(object):
    """
    Interface for health checks
    """

    def check(self): assert False

class NetworkAddress(object):
    """
    Represents the IP or DNS name associated with a service endpoint
    """
    def _init(self):
        self.host = None
        self.type = None

    def __init__(self, host, type):
        self._init()
        (self).host = host
        (self).type = type

    def toJSON(self):
        json = _JSONObject();
        (json).setObjectItem((u"host"), ((_JSONObject()).setString(self.host)));
        (json).setObjectItem((u"type"), ((_JSONObject()).setString(self.type)));
        return json

    def toString(self):
        return self.host


class ServicePort(object):
    """
    Represents the port associated with a service endpoint and the protocol it handles
    """
    def _init(self):
        self.name = None
        self.port = None

    def __init__(self, name, port):
        self._init()
        (self).name = name
        (self).port = port

    def toString(self):
        return ((self.name) + (u"-")) + (str(self.port))

    def toJSON(self):
        json = _JSONObject();
        (json).setObjectItem((u"name"), ((_JSONObject()).setString(self.name)));
        (json).setObjectItem((u"port"), ((_JSONObject()).setNumber(self.port)));
        (json).setObjectItem((u"secure"), ((_JSONObject()).setBool(False)));
        return json


class ServiceEndpoint(object):
    """
    Represents the combination of network address and service port.
    """
    def _init(self):
        self.name = None
        self.path = None
        self.address = None
        self.port = None

    def __init__(self, name, address, port):
        self._init()
        (self).name = name
        (self).address = address
        (self).port = port
        (self).path = u"/"

    def toString(self):
        return (((((self.port).name) + (u"://")) + ((self.address).host)) + (u":")) + (str((self.port).port))

    def toJSON(self):
        json = _JSONObject();
        (json).setObjectItem((u"name"), ((_JSONObject()).setString(self.name)));
        (json).setObjectItem((u"address"), ((self.address).toJSON()));
        (json).setObjectItem((u"port"), ((self.port).toJSON()));
        (json).setObjectItem((u"path"), ((_JSONObject()).setString(self.path)));
        return json


class ServiceRecord(object):
    """
    Maps a named service to a set of known endpoints.
    """
    def _init(self):
        self.name = None
        self.endpoints = None

    def __init__(self, name):
        self._init()
        (self).name = name
        (self).endpoints = _List()

    def toString(self):
        result = u"";
        header = (u"Record: ") + (self.name);
        pointer = u" --> ";
        result = (result) + (header)
        padding = u"";
        pdx = 0;
        while ((pdx) < (len(header))):
            padding = (padding) + (u" ")
            pdx = (pdx) + (1)

        edx = 0;
        while ((edx) < (len(self.endpoints))):
            if ((edx) != (0)):
                result = (result) + (padding)

            result = (((result) + (pointer)) + ((self.endpoints)[edx])) + (u"\n")
            edx = (edx) + (1)

        return result

    def toJson(self):
        json = _JSONObject();
        return json

