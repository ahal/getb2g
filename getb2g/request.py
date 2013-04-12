from base import valid_resources
from errors import InvalidResourceException
from handlers import all_handlers

__all__ = ('Request', 'valid_resources')

class Request(object):
    """Represents a set of actions to be performed"""
    resources = []
    state = {}

    def add_resource(self, resource, kwargs=None):
        kwargs = kwargs or {}
        if resource not in valid_resources:
            raise InvalidResourceException("The resource '%s' is not valid! Choose from: %s" %
                                                            (resource, ", ".join(valid_resources)))
        self.resources.add((resource, kwargs))

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
