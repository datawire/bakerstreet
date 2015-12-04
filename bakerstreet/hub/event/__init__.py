from quark_runtime import *

import hub
import hub.model


class RegistryEvent(object):
    """
    Base class for all Datawire Hub service registry events.
    """
    def _init(self):
        self.type = None
        self.timestamp = None

    def __init__(self, type):
        self._init()
        (self).type = type

    def dispatch(self, handler):
        (handler).onRegistryEvent(self);


class RegistryUpdate(RegistryEvent):
    """
    Represents an update to the service registry
    """
    def _init(self):
        RegistryEvent._init(self)
        self.records = _List([])
        self.data = None

    def __init__(self, type, json):
        super(RegistryUpdate, self).__init__(type);
        self.data = (json).toString()

    def dispatch(self, handler):
        (handler).onRegistryUpdate(self);


class RegistrySync(RegistryEvent):
    """
    Represents a registry synchronization sent to the client
    """
    def _init(self):
        RegistryEvent._init(self)
        self.data = None

    def __init__(self, type, json):
        super(RegistrySync, self).__init__(type);
        self.data = (json).toString()

    def dispatch(self, handler):
        (handler).onRegistrySync(self);


class RegistryJoin(RegistryEvent):
    def _init(self):
        RegistryEvent._init(self)

    def __init__(self, type, json):
        super(RegistryJoin, self).__init__(type);

    def dispatch(self, handler):
        (handler).onRegistryJoin(self);


class RegistryLeave(RegistryEvent):
    """
    Indicates a service endpoint has left or been removed from the registry
    """
    def _init(self):
        RegistryEvent._init(self)
        self.service = None
        self.id = None

    def __init__(self, type, json):
        super(RegistryLeave, self).__init__(type);
        (self).service = ((json).getObjectItem(u"")).getString()
        (self).id = ((json).getObjectItem(u"")).getString()

    def dispatch(self, handler):
        (handler).onRegistryLeave(self);

