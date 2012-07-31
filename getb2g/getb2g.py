from bs4 import BeautifulSoup
import ctypes
import getpass
import optparse
import os
import struct
import sys
import urllib2

_RELEASE_URI = "https://releases.mozilla.com"
_B2G_LATEST = _RELEASE_URI + "/b2g/latest"
_CHUNK_SIZE = 32768 

def find_url(user, password, device):
    """
    Returns the url of the build specified by device.
    """
    # install http basic auth opener
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='B2G Builds',
                              uri=_RELEASE_URI,
                              user=user,
                              passwd=password)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

    data = urllib2.urlopen(_B2G_LATEST)
    soup = BeautifulSoup(data.read())
    # ignore trunk builds
    link = soup.find_all('a', href=lambda x: device in x and 'trunk' not in x)[0]
    return _B2G_LATEST + '/' + link['href']

def _chunk_report(url, bytes_so_far, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("\rDownloading '%s' (%0.0f%%)" % (url, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')
    sys.stdout.flush()

def save_as(user, password, device, savepath, silent=False):
    """
    Finds the url of the build specified by device 
    and saves it to savepath.
    """
    url = find_url(user, password, device)
    
    response = urllib2.urlopen(url)
    total_size = int(response.info().getheader('Content-Length').strip())
    bytes_so_far = 0
    
    savepath = os.path.realpath(savepath)
    outfile = open(savepath, "wb")
    while True:
        chunk = response.read(_CHUNK_SIZE)
        if not chunk:
             break
        
        bytes_so_far += len(chunk)
        outfile.write(chunk)

        if not silent:
            _chunk_report(url, bytes_so_far, total_size)
    
    outfile.close()
    return savepath

def cli(args=sys.argv[1:]):
    valid_devices = ['emulator-arm',
                     'emulator-x86', 
                     'nexus-s',
                     'otoro',
                     'sgs2']

    parser = optparse.OptionParser(usage="%prog [options]")
    parser.add_option("--user", dest="user",
                      action="store", default=getpass.getuser(),
                      help="Username for the b2g nightly releases")
    parser.add_option("--password", dest="password",
                      action="store", default=None,
                      help="Password for the b2g nightly releases")
    parser.add_option("--device", dest="device",
                      action="store", default=None,
                      help="Device for which to get build. "
                           "One of %s" % ", ".join(valid_devices))
    parser.add_option("-o", "--output-file", dest="outfile",
                      action="store", default=None,
                      help="File path to save the build. If not specified, "
                           "the URL will be printed to stdout.")

    opt, arguments = parser.parse_args(args)
   
    # verify options
    if not opt.device in valid_devices:
        print "Specify a valid device with --device: %s" % ", ".join(valid_devices)
        return 1
    if not opt.password:
        opt.password = getpass.getpass("Password for %s:" % opt.user)

    if not opt.outfile:
        print find_url(opt.user, opt.password, opt.device)
    else:
        print save_as(opt.user, opt.password, opt.device, opt.outfile)


if __name__ == '__main__':
    sys.exit(cli())
