from handlers import all_handlers

__all__ = ('Request', 'InvalidResourceException', 'valid_resources')

valid_resources = ('gecko',
                   'emulator',
                   'busybox',
                   'minidump_stackwalk',
                   'tests')

class InvalidResourceException(Exception):
    """The requested resource was not valid"""

class IncompleteRequestException(Exception):
    """The requested resource was not valid"""

class Request(object):
    """Represents a set of actions to be performed"""
    resources = []
    state = {}

    def add_resource(self, resource, args=None, kwargs=None):
        args = args or []
        kwargs = kwargs or {}
        if resource not in valid_resources:
            raise InvalidResourceException("The resource '%s' is not valid! Choose from: %s" %
                                                            (resource, ", ".join(valid_resources)))
        self.resources.add((resource, args, kwargs))

    def dispatch(self, handlers=all_handlers):
        potential_handlers = []
        for handler in handlers:
            handled_resources = handler.handled_resources(self)
            potential_handlers.append((handler, handled_resources))

        potential_handlers.sort(key=lambda x: len(x[1]))
        for handler in potential_handlers:
            if len(self.resources) > 0:
                handler.execute_request(self)
        
        if len(self.resources) > 0:
            print "Sorry, we were unable to find an appropriate handler for these resources: %s" % ", ".join(self.resources)
