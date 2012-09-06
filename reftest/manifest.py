import optparse
import os
import sys

class ReftestManifestChanger():
    def __init__(self, server_url, gecko_path):
        self.server = server_url
        self.gecko = gecko_path

    def parse_logs(self, log_list, callback):
        """
        log_list - list of log files to parse
        """
        ret = [] 
        for log in log_list:
            if not os.path.isfile(log) or not log.endswith('.log'):
                continue
            
            f = open(log, 'r')
            for line in f.readlines():
                line = line.strip()
                if callback(line) and line.find(self.server) != -1:
                    index = line.index(self.server) + len(self.server)
                    test = line[index:line.find(' ', index)]
                    desc = line[line.rindex('|') + 1:].strip()
                    ret.append((test, desc))
            f.close()
        return ret


    def edit_manifests(self, fails, callback):
        for fail in fails:
            print fail
            (subdir, test) = os.path.split(fail[0])
            path = os.path.join(self.gecko, subdir, 'reftest.list')
            m = open(path, 'r')
            lines = m.readlines()
            m.close()
            for index, line in enumerate(lines):
                if line.find(test) != -1:
                    if fail[1].find("image comparison") != -1 and line.find(fail[1][-3:-2]) == -1:
                        continue
                    lines[index] = callback(line.strip())
                    break
            m = open(path, 'w')
            m.writelines(lines)
            m.close()


def run(args=sys.argv[1:]):
    parser = optparse.OptionParser(usage="%prog [options]")
    parser.add_option("--log-dir", dest="log_dir",
                      default=None,
                      help="directory containing the logs to parse")
    parser.add_option("--server-url", dest="server_url",
                      default=None,
                      help="url of the webserver root")
    parser.add_option("--gecko-path", dest="gecko_path",
                      default=None,
                      help="path to gecko root directory (i.e mozilla-central)")
   
    opt, arguments = parser.parse_args(args)

    changer = ReftestManifestChanger(opt.server_url, opt.gecko_path)
    tests = changer.parse_logs([os.path.join(opt.log_dir, l) for l in os.listdir(opt.log_dir)], lambda x: True if x.find("TEST-UNEXPECTED-FAIL") != -1 else False)
    import json
    print json.dumps(tests, indent=2)
    changer.edit_manifests(tests, lambda x: "skip-if(B2G) %s # bug 773482\n" % x if x.find('B2G') == -1 else "%s\n" % x)

if __name__ == '__main__':
    sys.exit(run())
