import json
import optparse
import os
import sys

def parse(logfile, resolution=None):
    width = 0
    height = 0
    if resolution:
        width, height = [int(val) for val in resolution.split('x', 1)]

    with open(logfile, 'r') as log:
        lines = [l.strip() for l in log.readlines() if l.find('Canvas dimensions') != -1]

    total = 0
    tests = []
    for line in lines:
        tokens = line.split()
        w = int(tokens[9].strip(', '))
        h = int(tokens[11].strip())
        if (w > width or h > height):
            tests.append({'name':tokens[6],'width':w,'height':h})
            total += 1

    result = {'tests': tests, 'total': total}
    return result

def cli(args=sys.argv[1:]):
    parser = optparse.OptionParser(usage="%prog [options]")

    parser.add_option('--log', dest='log',
                      help='Path to the reftest log file to parse')
    parser.add_option('-r', '--resolution', dest='res',
                      default=None,
                      help='Resolution in the form <width>x<height>. '
                           'Tests requiring greater resolutions will be dumped. '
                           'If not specified, all tests will be dumped.')

    opt, args = parser.parse_args(args)

    if not opt.log or not os.path.isfile(opt.log):
        parser.error("Log file '%s' is not valid" % opt.log) 

    print json.dumps(parse(opt.log, opt.res), indent=2)

if __name__ == '__main__':
    sys.exit(cli())
