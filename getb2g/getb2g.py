#!/usr/bin/env python
"""GetB2G is a module designed to set up everything you need
to run B2G builds and tests in one convenient directory. You 
can run with no additional arguments to be dropped into an 
interactive session designed to help figure out what you need.
"""

import optparse
import os
import sys

from base import valid_resources
from errors import MultipleDeviceResourceException
from prompt import prompt_resources 
from request import Request
import prompt
import mozlog
log = mozlog.getLogger('GetB2G')

def build_request(resources, metadata={}):
    request = Request(metadata=metadata)
    for resource in resources:
        request.add_resource(resource)
    request.dispatch()

def cli(args=sys.argv[1:]):
    parser = optparse.OptionParser(usage='%prog [options]', description=__doc__)

    parser.add_option('-d', '--workdir', dest='workdir',
                      action='store', default=os.path.join(os.getcwd(), 'b2g-workdir'),
                      help='Set up everything in this directory')
    parser.add_option('--no-prompt', dest='prompt_disabled',
                      action='store_true', default=False,
                      help='Never prompt me for any additional '
                           'information, error out instead')
    parser.add_option('--only', dest='only',
                      action='store_true', default=False,
                      help='Only prepare resources I explicitly specify (either by '
                           'command line or prompt)')
    parser.add_option('--log-level', dest='log_level', action='store',
                      type='choice', default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                      help='Only print messages at this log level')
    for resource in valid_resources['cli'].difference(valid_resources['default']):
        cmdlet = resource.replace('_', '-')
        parser.add_option('--prepare-%s' % cmdlet, dest=resource,
                          action='store_true', default=False,
                          help='Do whatever it takes to set up %s' % resource)
    parser.add_option('-m', '--metadata', dest='metadata',
                      action='append', default=[],
                      help='Append a piece of metadata in the form <key>=<value>. ' 
                           'Attempt to use this metadata wherever it makes sense. '
                           'Store values of duplicate keys in a list. E.g --metadata '
                           'user=foo --metadata user=bar --metadata branch=mozilla-central')
    options, args = parser.parse_args(args)
    log.setLevel(getattr(mozlog, options.log_level))
    prompt.prompt_disabled = options.prompt_disabled

    metadata = {}
    if not os.path.isdir(options.workdir):
        os.makedirs(options.workdir)
    metadata['workdir'] = options.workdir
    for data in options.metadata:
        k, v = data.split('=', 1)
        if k in metadata:
            if not isinstance(metadata[k], list):
                metadata[k] = [metadata[k]]
            metadata[k].append(v)
        else:
            metadata[k] = v
   
    resources = set([r for r in valid_resources['all'] if getattr(options, r, False)])
    device = resources.intersection(valid_resources['device'])
    if len(device) > 1:
        raise MultipleDeviceResourceException(*device)

    if not options.only:
        resources.update(valid_resources['default'])
    resources = prompt_resources(valid_resources, resources)

    if not options.only:
        def add_dependencies(res):
            for r in valid_resources[res]:
                if res in resources:
                    resources.add(r)
                if r in valid_resources:
                    add_dependencies(r)
        t_resources = resources.copy()
        for res in t_resources:
            if res in valid_resources:
                add_dependencies(res)

    build_request(resources, metadata)

if __name__ == '__main__':
    sys.exit(cli())
