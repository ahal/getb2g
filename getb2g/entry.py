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
from prompt import prompt_resources 
from request import Request

def build_request(resources, metadata={}):
    request = Request()
    for resource in resources:
        request.add(resource, metadata)
    request.dispatch()

def cli(args=sys.argv[1:]):
    parser = optparse.OptionParser(usage='%prog [options]', description=__doc__)

    parser.add_option('-d', '--workdir', dest='workdir',
                      action='store', default=None,
                      help='
    parser.add_option('--no-prompt', dest='prompt_disabled',
                      action='store_true', default=False,
                      help='Never prompt me for any additional '
                           'information. If vital information is missing, '
                           'raise an exception instead.')
    parser.add_option('--damnit', dest='damnit',
                      action='store_true', default=False,
                      help='Just give me something that I can use to test B2G damnit!')
    for resource in valid_resources:
        resource = resource.replace('_', '-')
        parser.add_option('--prepare-%s' % resource, dest=resource,
                          action='store_true', default=False,
                          help='Do whatever it takes (download, checkout, extract, etc.) '
                               'to set up %s' % resource)
    parser.add_option('-m', '--metadata', dest='metadata',
                      action='append', default=[],
                      help='Append a piece of metadata in the form <key>=<value>. ' 
                           'Attempt to use this metadata wherever it makes sense. '
                           'Store values of duplicate keys in a list. E.g --metadata '
                           'user=foo --metadata user=bar --metadata branch=mozilla-central')
    options, args = parser.parse_args(args)

    metadata = {}
    for data in options.metadata:
        k, v = data.split('=', 1)
        if k in metadata:
            if not isinstance(metadata[k], list):
                metadata[k] = [metadata[k]]
            metadata[k].append(v)
        else:
            metadata[k] = v
    
    if options.damnit:
        resources = ('emulator', 'symbols', 'busybox', 'tests', 'minidump_stackwalk')
        return build_request(resouces, metadata)

    resources = [r for r in valid_resources if hasattr(options, r)]
    if not options.prompt_disabled:
        resources, metadata = start_prompt(resources, metadata)

    build_request(resources, metadata)

if __name__ == '__main__':
    sys.exit(cli())
