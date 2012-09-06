"""
Runs each manifest in the root reftest.list separately and saves the log files
Needs to be run from the objdir/_tests/reftest directory
"""
from bs4 import BeautifulSoup
from b2gautomation import B2GRemoteAutomation
from logparser import LogParser
from time import sleep
from runreftestb2g import B2GOptions
import autolog
import mozlog
import runreftestb2g
import shutil
import sys
import os
import urllib2
import uuid

here = os.path.realpath(os.path.dirname(__file__))

def run(manifests, output_dir, args, post_to_autolog=False):
    args = args[:]
    log = mozlog.getLogger('REFTEST')

    # set up chunks in args list
    try:
        this_index = args.index("--this-chunk")
        this_chunk = int(args[this_index+1])
        total_chunks = this_chunk
    except:
        this_index = len(args)
        this_chunk = 1
        args.append("--this-chunk")
        args.append("1")
        try:
            total_index = args.index("--total-chunks")
        except:
            total_index = len(args)
            args.append("--total-chunks")
            args.append(str(this_chunk))
        total_chunks = int(args[total_index+1])

    b2g_path = args[args.index("--b2gpath")+1]
    # symlink reftests so reftest server can serve them
    if not os.path.exists('tests'):
        gecko_path = os.path.join(b2g_path, 'gecko')
        os.symlink(gecko_path, 'tests')
    
    # get revision
    default = open(os.path.join(b2g_path, 'default.xml'), 'r')
    soup = BeautifulSoup(default.read())
    mc = soup.find_all('project', attrs={'name':'mozilla-central'})[0]
    revision = mc['revision']
    
    with open(manifests, "r") as manifest_file:
        manifests = manifest_file.readlines()
    
    args.append('')
    for manifest in manifests:
        manifest = manifest.strip()
        if manifest[0] == '#':
            continue
        manifest_path = os.path.join('tests', 'layout', 'reftests', manifest)
        args[-1] = manifest_path

        for chunk in range(this_chunk, total_chunks + 1):
            args[this_index + 1] = str(chunk)
            log.info("Running with manifest '%s' and chunk '%s' of '%s'" % (manifest_path, chunk, total_chunks))
            ret = runreftestb2g.main(args)
            log.info("Run finished with return value '%s'" % ret)
            sleep(5)
        
            if os.path.exists('reftest.log'):
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                output_file = manifest.replace('/', '_').replace('.list', '%s_of_%s.log' % (chunk, total_chunks))
                log_file = os.path.join(output_dir, output_file)
                shutil.move('reftest.log', log_file)
               
                # send log file to autolog
                if post_to_autolog:
                    parser = LogParser([log_file], harnessType='reftest')
                    results = parser.parseFiles()
                    results['id'] = str(uuid.uuid1())
                    try:
                        autolog.post_to_autolog(results,
                                                'reftests-%s' % chunk,
                                                revision,
                                                log_file,
                                                'reftest')
                    except urllib2.HTTPError:
                        # autolog times out sometimes, try again
                        autolog.post_to_autolog(results,
                                                'reftests-%s' % chunk,
                                                revision,
                                                log_file,
                                                'reftest')

            else:
                log.error("No reftest.log! :(")

    log.info("Test Runs Completed")

class ReftestRunnerOptions(B2GOptions):
    def __init__(self, automation, **kwargs):
        B2GOptions.__init__(self, automation) 
        self.add_option('--manifest-list', dest='manifests', action='store',
                            default=None,
                            help='List of reftest manifests to run')
        self.add_option('--output-dir', dest='output_dir', action='store',
                            default=os.path.join(here, 'reftest_logs'),
                            help='Directory to store the log files')

    def parse_args(self, args):
        opt, arguments = B2GOptions.parse_args(args)
        if not opt.manifests:
            self.error("must specify --manifest-list")
        return opt, arguments


def cli(args=sys.argv[1:]):
    auto = B2GRemoteAutomation(None, 'fennec') 
    parser = ReftestRunnerOptions(auto)
    opt, arguments  = parser.parse_args(args)

    try:
        index = args.index("--manifest-list")
        args.pop(index)
        args.pop(index)
    except:
        pass

    try:
        index = args.index("--output-dir")
        args.pop(index)
        args.pop(index)
    except:
        pass
    

    run(opt.manifests, opt.output_dir, args)

 

if __name__== '__main__':
    sys.exit(run(sys.argv[1:]))
