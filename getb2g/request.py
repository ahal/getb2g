from base import valid_resources
from errors import InvalidResourceException
import handlers

__all__ = ('Request', 'valid_resources')

class Request(object):
    """Represents a set of actions to be performed"""
    resources = []
    state = {}

    def add_resource(self, resource, kwargs=None):
        kwargs = kwargs or {}
        if resource not in valid_resources['all']:
            raise InvalidResourceException("The resource '%s' is not valid! Choose from: %s" %
                                                            (resource, ", ".join(valid_resources['all'])))
        self.resources.append((resource, kwargs))

    def dispatch(self):
        potential_handlers = []
        for handler in handlers.all_handlers:
            handled_resources = getattr(handlers, handler).handled_resources(self)
            potential_handlers.append((handler, handled_resources))

        print "potential_handlers: %s" % potential_handlers

        potential_handlers.sort(key=lambda x: len(x[1]))
        for handler, resources in potential_handlers:
            if len(self.resources) > 0:
                getattr(handlers, handler).execute_request(self)
        
        if len(self.resources) > 0:
            print "Sorry, we were unable to find an appropriate handler for these resources: %s" % ", ".join([r[0] for r in self.resources])
