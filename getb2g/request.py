from base import valid_resources
from errors import InvalidResourceException
import handlers

__all__ = ('Request', 'valid_resources')

class Request(object):
    """Represents a set of actions to be performed"""
    resources = []
    def __init__(self, metadata=None):
        self.metadata = metadata or {}

    def add_resource(self, resource):
        if resource not in valid_resources['all']:
            raise InvalidResourceException("The resource '%s' is not valid! Choose from: %s" %
                                                            (resource, ", ".join(valid_resources['all'])))
        self.resources.append(resource)

    def dispatch(self):
        potential_handlers = []
        for handler in handlers.all_handlers:
            handled_resources = getattr(handlers, handler).handled_resources(self)
            potential_handlers.append((handler, handled_resources))

        potential_handlers.sort(key=lambda x: len(x[1]))
        for handler, resources in potential_handlers:
            if len(self.resources) > 0:
                getattr(handlers, handler).execute_request(self)
        
        if len(self.resources) > 0:
            print "Sorry, we were unable to find an appropriate handler for these resources: %s" % ", ".join([r for r in self.resources])
