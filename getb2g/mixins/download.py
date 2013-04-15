import os
import sys
import urllib2
import urlparse

from ..errors import MissingDataException
from .. import prompt

import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ('DownloadMixin')

class DownloadMixin(object):
    """Mixin for downloading files"""
    _CHUNK_SIZE = 1048576

    def install_basic_auth(self, url, user=None, password=None):
        user = user or self.data.get('user')
        password = password or self.data.get('password')
        user, password = prompt.prompt_user_pass(url, user, password)

        if None in (url, user, password):
            raise MissingDataException()

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='B2G Builds',
                                  uri=url,
                                  user=user,
                                  passwd=password)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
    
    def get_filename_from_url(self, url):
        parsed = urlparse.urlsplit(url.rstrip('/'))
        if parsed.path != '':
            return parsed.path.rsplit('/', 1)[-1]
        else:
            return parsed.netloc

    def _chunk_report(self, bytes_so_far, total_size):
        percent = float(bytes_so_far) / total_size
        percent = round(percent * 100, 2)
        if log.level <= mozlog.INFO:
            sys.stdout.write("\r%s of %s bytes (%0.0f%%)" % (bytes_so_far, total_size, percent))
        if bytes_so_far >= total_size:
            sys.stdout.write("\n")
        sys.stdout.flush()

    
    def download_file(self, url, file_name=None):
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            if e.code == 401:
                s = urlparse.urlparse(url)
                self.install_basic_auth(url='%s://%s' % (s.scheme, s.netloc))
                return self.download_file(url, file_name)
            else:
                raise

        log.info('downloading %s' % url)
        workdir = self.data.get('workdir')

        try:
            total_size = int(response.info().getheader('Content-Length').strip())
        except AttributeError:
            total_size = 0
        bytes_so_far = 0

        if not file_name:
            file_name = self.get_filename_from_url(url)

        if os.path.isdir(file_name):
            dest = os.path.join(workdir, file_name, self.get_filename_from_url(url))
        else:
            dest = os.path.join(workdir, file_name)
            
        local_file = open(dest, 'wb')
        while True:
            chunk = response.read(self._CHUNK_SIZE)
            if not chunk:
                break
            bytes_so_far += len(chunk)
            local_file.write(chunk)


            if total_size:
                self._chunk_report(bytes_so_far, total_size)
        local_file.close()
        return dest
