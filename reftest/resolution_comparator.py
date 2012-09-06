from resolution_parser import parse
from time import sleep
import json
import marionette
import mozhttpd
import optparse
import os
import shutil
import sys

def run(args=sys.argv[1:]):
    parser = optparse.OptionParser(usage="%prog [options]")
    parser.add_option('--gecko-path', dest='gecko',
                      default=None,
                      help='Path to the root gecko directory containing the reftests')
    parser.add_option('--server-port', dest='port',
                      default='8888',
                      help='Port the httpd server should use')
    parser.add_option('-i', '--input-file', dest='infile',
                      default=None,
                      help='Path to a reftest log file containing canvas dimensions')
    parser.add_option('-r', '--resolution', dest='res',
                      default=None,
                      help='The resolution in the form of <width>x<height>')
    parser.add_option('-o', '--output-file', dest='output',
                     default=None,
                     help='Path to output file')

    opt, args = parser.parse_args(args)
    if not os.path.isdir(opt.gecko):
        parser.error("Gecko path '%s' is not a valid directory" % opt.gecko)

    if not os.path.isfile(opt.infile):
        parser.error("Input file '%s' is not a valid file" % opt.infile)

    if not opt.res:
        parser.error("Must specify a resolution")

    width, height = [int(val) for val in opt.res.split('x', 1)]
    
    if not opt.output:
        opt.output = '%sx%s_tests_to_fix.txt' % (width, height)

    try:
        with open(opt.infile, 'r') as f:
            temp = json.loads(f.read())
            obj = {'total': 0, 'tests': []}
            total = 0
            for t in temp['tests']:
                if t['width'] > width or t['height'] > height:
                    obj['tests'].append(t)
                    total += 1
            obj['total'] = total
    except ValueError:
        obj = parse(opt.infile, opt.res)

    print json.dumps(obj, indent=2)

    res_file = 'reftest_resolution.html'
    with open(os.path.join(opt.gecko, res_file), 'w') as f:
        f.write("""
                <html>
                    <head>
                        <style type='text/css'>
                            iframe {
                                overflow: hidden;
                            }
                            #frame1 {
                                float: left;
                                width: 800px;
                                height: 1000px;
                                min-width: 800px;
                                min-height: 1000px;
                                margin-right: 40px;
                            }
                        </style>
                    </head>
                    <body>
                        <iframe id='frame1'></iframe>
                        <iframe id='frame2'></iframe>
                    </body>
                </html>
                """)

    shutil.copyfile(res_file, os.path.join(opt.gecko, res_file)) 

    server = mozhttpd.MozHttpd(docroot=opt.gecko, port=opt.port)
    server.start(block=False)

    # hacky code to get relative path
    index = -1
    for test in obj['tests']:
        index = test['name'].find('layout')
        if index != -1:
            break

    for test in obj['tests']:
        test['name'] = test['name'][index:]

    client = marionette.Marionette(host='localhost', port=2828)
    client.start_session()
    client.set_context("chrome")
    client.execute_script("""
        var perms = Components.classes["@mozilla.org/permissionmanager;1"].getService(Components.interfaces.nsIPermissionManager);
        var ioService = Components.classes["@mozilla.org/network/io-service;1"].getService(Components.interfaces.nsIIOService);
        var uri = ioService.newURI("http://localhost:%s", null, null);
        perms.add(uri, "allowXULXBL", Components.interfaces.nsIPermissionManager.ALLOW_ACTION);
    """ % opt.port)
    client.set_context("content")

    url = "http://127.0.0.1:%s" % opt.port
    client.navigate("%s/%s" % (url, res_file))
    client.execute_script("""
        let frame = window.document.getElementById('frame2');
        frame.setAttribute('style', 'width:%s;min-width:%s;height:%s;min-height:%s');
        """ % (width, width, height, height))

    need_fixing = { 'total': 0, 'tests': [] }
    total = 0
    for test in obj['tests']:
        location = "%s/%s" % (url, test['name'])
        print location
        client.execute_script("""
            let frame1 = window.document.getElementById('frame1');
            let frame2 = window.document.getElementById('frame2');
            frame1.setAttribute('src', '%s');
            frame2.setAttribute('src', '%s');
            """ % (location, location))
        while True:
            fix = raw_input("Does this test need to be fixed? (y/N): ")
            if fix.lower().strip() == 'w':
                need_fixing['total'] = total
                with open(opt.output, 'w') as f:
                    f.write(json.dumps(need_fixing, indent=2))
            elif fix.lower().strip() == 'y':
                need_fixing['tests'].append(test)
                total += 1
                break
            elif fix.lower().strip() == 'n' or fix.lower().strip() == '':
                break

    need_fixing['total'] = total
    with open(opt.output, 'w') as f:
        f.write(json.dumps(need_fixing, indent=2))

    server.stop()
    os.remove(os.path.join(opt.gecko, res_file))

if __name__ == '__main__':
    sys.exit(run())
