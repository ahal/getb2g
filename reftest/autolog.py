# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from logparser import LogParser
from mozautolog import RESTfulAutologTestGroup as AutologTestGroup
from mozprocess.processhandler import ProcessHandler
from optparse import OptionParser
import json
import os
import socket
import sys
import uuid

def post_to_autolog(data, testgroup, revision=None, logfile=None, harness='mochitest'):
    testgroup = AutologTestGroup(machine=socket.gethostname(),
                                 id=data['id'],
                                 platform='emulator',
                                 os='android',
                                 harness='autolog',
                                 testgroup=testgroup,
                                 logfile=logfile,
                                )

    testgroup.set_primary_product(tree='b2g',
                                  revision=revision,
                                  buildtype='opt',
                                 )

    testgroup.add_test_suite(testsuite=harness,
                             passed=data.get('passed', 0),
                             failed=data.get('failed', 0),
                             todo=data.get('todo', 0),
                             id="%s-testsuite1" % data['id'],
                            )

    for tf_index, failure in enumerate(data.get('failures', [])):
        for f in failure.get('failures', []):
            testgroup.add_test_failure(test=failure.get('test', None),
                                       id="%s-testfailure1.%d" % (data['id'], (tf_index+1)),
                                       duration=failure.get('duration', None),
                                       **f
                                      )

    testgroup.submit()


def main():
    parser = OptionParser()
    parser.add_option('--harness', dest='harness', action='store',
                      default='mochitest',
                      help='test harness log being parsed. ' +
                           'one of build, mochitest, reftest, jsreftest, crashtest or xpcshell')
    parser.add_option('--logfile', dest='logfile', action='store',
                      default=None,
                      help='path to log file')
    parser.add_option('--revision', dest='commit', action='store',
                      help='repo revision')
    parser.add_option('--autolog', dest='autolog', action='store_true',
                      help='post results to autolog')
    parser.add_option('--testgroup', dest='testgroup', action='store',
                      help='testgroup name for autolog')

    options, args = parser.parse_args()

    # set default log file
    if not options.logfile:
        options.logfile = options.harness + '.log'
    options.logfile = os.path.abspath(options.logfile)

    if options.autolog and not options.commit:
        raise Exception('must specify --revision if --autolog is used')

    if options.autolog and not options.testgroup:
        raise Exception('must specify --testgroup if --autolog is used')

    # parse the logfile, which will give us a nice dict of results
    parser = LogParser([options.logfile], harnessType=options.harness)
    results = parser.parseFiles()
    results['id'] = str(uuid.uuid1())
    print json.dumps(results, indent=2)

    # post the results to autolog
    if options.autolog:
        post_to_autolog(results,
                        options.testgroup,
                        logfile=options.logfile,
                        revision=options.commit,
                        harness=options.harness)

if __name__ == "__main__":
    sys.exit(main())

