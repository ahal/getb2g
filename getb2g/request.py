import os
import shutil

from base import valid_resources
from errors import InvalidResourceException, MultipleDeviceResourceException
import handlers

import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ('Request', 'valid_resources')

class Request(object):
    """Represents a set of actions to be performed"""
    resources = []
    def __init__(self, metadata=None):
        self.metadata = metadata or {}

    def add_resource(self, resource):
        if resource not in valid_resources['all']:
            raise InvalidResourceException(msg="The resource '%s' is not valid! Choose from: %s" %
                                                            (resource, ", ".join(valid_resources['all'])))
        self.resources.append(resource)
        if resource in valid_resources['device']:
            if 'device' in self.metadata:
                raise MultipleDeviceResourceException(self.metadata['device'], resource)
            self.metadata['device'] = resource
            self.metadata['workdir'] = os.path.join(self.metadata['workdir'], resource)
            if os.path.isdir(self.metadata['workdir']):
                shutil.rmtree(self.metadata['workdir'])
            os.makedirs(self.metadata['workdir'])

    def dispatch(self):
        """
        Request dispatches itself by calling execute_request on each of the required handlers
        """
        potential_handlers = []
        for handler in handlers.all_handlers:
            num_res = len(getattr(handlers, handler).handled_resources(self))
            if num_res > 0:
                potential_handlers.append((handler, num_res))

        # sort the handlers based on how many resources they can handle,
        # we want to use as few as possible so resources come from the same place 
        potential_handlers.sort(key=lambda x: x[1], reverse=True)
        for handler, num_res in potential_handlers:
            if len(self.resources) > 0:
                getattr(handlers, handler).execute_request(self)
        
        if len(self.resources) > 0:
            log.error("Sorry, unable to prepare any of these resources: %s" % ", ".join([r for r in self.resources]))
        log.info("Jobs done! Take a look in '%s' to see your files!" % self.metadata['workdir'])
