import os
import shutil
import sys
import urllib2
import urlparse

from ..errors import MissingDataException
from ..prompt import prompt_user_pass

import mozfile
import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ('DownloadMixin',)

class DownloadMixin(object):
    """Mixin for downloading files"""
    _CHUNK_SIZE = 1048576
    _first_print = ''

    def install_basic_auth(self, url, user=None, password=None):
        user = user or self.metadata.get('user')
        password = password or self.metadata.get('password')

        if None in (url, user, password):
            raise MissingDataException()

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, user, password)
        auth_handler = urllib2.HTTPBasicAuthHandler(passman)
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
            percent = '(%0.0f%%)' % percent
            sys.stdout.write('%s %s' % (self._first_print, percent))
            self._first_print = '\b' * (len(percent) + 1)
        if bytes_so_far >= total_size:
            sys.stdout.write('\n')
        sys.stdout.flush()

    def download_extract(self, url, file_name=None, silent=False, outdir=None):
        file_name = self.download_file(url, file_name=file_name, silent=silent)
        files = mozfile.extract(file_name)
        os.remove(file_name)

        if not outdir and len(files) > 1:
            name = os.path.basename(file_name)
            for suffix in ('.zip', '.tar.gz', '.tar.bz2'):
                if name.endswith(suffix):
                     outdir = name[:-len(suffix)]
                     break

        if outdir:
            outdir = os.path.join(self.metadata['workdir'], outdir)
            if os.path.isdir(outdir):
                shutil.rmtree(outdir)

            if len(files) == 1:
                shutil.move(files[0], outdir)
            elif len(files) > 1:
                os.makedirs(outdir)
                for f in files:
                    shutil.move(f, os.path.join(outdir, os.path.basename(f)))
        log.debug("extracted '%s' to '%s'" % (file_name, outdir or files[0]))


    def download_file(self, url, file_name=None, silent=False):
        if hasattr(url, '__call__'):
            url = self.get_resource_url(url)

        domain = urlparse.urlparse(url)
        domain = '%s://%s' % (domain.scheme, domain.netloc)
        auth = self.load_auth(domain)

        for user, passwd in auth:
            self.install_basic_auth(url=url, user=user, password=passwd)

        user = None
        password = None
        while True:
            try:
                response = urllib2.urlopen(url)
                break
            except urllib2.HTTPError, e:
                if e.code == 401:
                    user, password = prompt_user_pass(url)
                    if None in (user, password):
                        raise
                    self.install_basic_auth(url=url, user=user, password=password)
                else:
                    raise

        if None not in (user, password):
            self.save_auth(domain, user, password)

        workdir = self.metadata.get('workdir')
        try:
            total_size = int(response.info().getheader('Content-Length').strip())
        except AttributeError:
            total_size = 0
        bytes_so_far = 0

        if not file_name:
            file_name = self.get_filename_from_url(url)

        if os.path.isdir(os.path.join(workdir, file_name)):
            dest = os.path.join(workdir, file_name, self.get_filename_from_url(url))
        else:
            dest = os.path.join(workdir, file_name)

        local_file = open(dest, 'wb')

        # format the message without actually logging it
        fn, lno, func = log.findCaller()
        record = log.makeRecord(log.name, mozlog.INFO, fn, lno, 'downloading %s', url, None)
        h = log.handlers[0]
        self._first_print = h.format(record)
        while True:
            chunk = response.read(self._CHUNK_SIZE)
            if not chunk:
                break
            bytes_so_far += len(chunk)
            local_file.write(chunk)


            if total_size and not silent:
                self._chunk_report(bytes_so_far, total_size)
        local_file.close()
        return dest
