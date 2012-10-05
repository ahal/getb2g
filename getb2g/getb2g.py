from bs4 import BeautifulSoup
import ctypes
import getpass
import optparse
import os
import struct
import sys
import urllib2

_RELEASE_URI = "https://releases.mozilla.com/b2g/"
_B2G_LATEST = "latest"
_CHUNK_SIZE = 32768

def find_url(user, password, keys, date=None, silent=False):
    """
    Returns the url of the build specified by keys or None.
    """
    # install http basic auth opener
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='B2G Builds',
                              uri=_RELEASE_URI,
                              user=user,
                              passwd=password)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

    if not date:
        uri = _RELEASE_URI + _B2G_LATEST
    else:
        uri = _RELEASE_URI + date

    try:
        data = urllib2.urlopen(uri)
    except urllib2.HTTPError, e:
        if not silent:
            print "Failed to open uri: %s" % e
        return None
    soup = BeautifulSoup(data.read())
    # get trunk build if it exists
    try:
        link = soup.find_all('a', href=lambda x: len(keys) == len([k for k in keys if k in x]))[0]
    except:
        return None
    return uri + '/' + link['href']

def _chunk_report(bytes_so_far, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("\rDownloading (%0.0f%%)" % percent)

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')
    sys.stdout.flush()

def save_as(user, password, keys, savepath, date=None, silent=False):
    """
    Finds the url of the build specified by device
    and saves it to savepath.

    If no builds were found, returns None
    """
    url = find_url(user, password, keys, date=date, silent=silent)
    if url is None:
        if not silent:
            print "Could not find build matching [%s]" % ", ".join(keys)
        return None

    response = urllib2.urlopen(url)
    total_size = int(response.info().getheader('Content-Length').strip())
    bytes_so_far = 0

    savepath = os.path.realpath(savepath)
    outfile = open(savepath, "wb")

    if not silent:
        print url
    while True:
        chunk = response.read(_CHUNK_SIZE)
        if not chunk:
             break

        bytes_so_far += len(chunk)
        outfile.write(chunk)

        if not silent:
            _chunk_report(bytes_so_far, total_size)

    outfile.close()
    return savepath

def cli(args=sys.argv[1:]):
    parser = optparse.OptionParser(usage="%prog [options]")
    parser.add_option("-u", "--user", dest="user",
                      action="store", default=getpass.getuser(),
                      help="Username for the b2g nightly releases")
    parser.add_option("--key", dest="keys",
                      action="append", default=None,
                      help="List of keywords to use for finding which "
                           " build to get. First build which matches all is chosen")
    parser.add_option("-o", "--output-file", dest="outfile",
                      action="store", default=None,
                      help="File path to save the build. If not specified, "
                           "the URL will be printed to stdout")
    parser.add_option("--date", dest="date",
                      action="store", default=None,
                      help="Date of the nightly to download in the format: "
                           "YYYY-MM-DD")

    opt, arguments = parser.parse_args(args)

    # verify options
    if not opt.keys:
        parser.error("Must specify at least one --key")
        return 1

    password = getpass.getpass("Password for %s:" % opt.user)

    if not opt.outfile:
        url = find_url(opt.user, password, opt.keys, date=opt.date)
    else:
        url = save_as(opt.user, password, opt.keys, opt.outfile, date=opt.date)
    
    if url is not None:
        print url

if __name__ == '__main__':
    sys.exit(cli())
