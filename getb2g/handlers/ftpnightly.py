import os
import shutil
from ..base import (Base, TestBase, B2GDesktopBase)
from ..mixins import TinderboxMixin, DateMixin

import mozfile
import mozinfo
import mozinstall

__all__ = ['FtpNightlyHandler']

class FtpNightlyHandler(Base, B2GDesktopBase, TestBase, TinderboxMixin, DateMixin):
    """
    Handles nightly builds from ftp.m.o/pub/mozilla.org/b2g/nightly
    """
    _base_url = 'http://ftp.mozilla.org/pub/mozilla.org/b2g/nightly'
    _device_names = { 'b2g_desktop' : 'b2g' }
    _platform = None
    suffix = 'tar.bz2'

    @property
    def url(self):
        if self._url:
            return self._url

        if 'build_dir' in self.metadata:
            self._url = self.metadata['build_dir']
            return self._url

        url = '%s/%s-%s/' % (self._base_url, '%s', self.branch)
        self._url = self.get_date_url(url)
        return self._url

    @property
    def platform(self):
        if not self._platform:
            self._platform = self.metadata.get('platform')
            if self._platform:
                return self._platform

            if mozinfo.isLinux:
                self._platform = 'linux-%s' % 'x86_64' if mozinfo.bits == 64 else 'i686'
                self.suffix = 'tar.bz2'
            elif mozinfo.isMac:
                self._platform = 'mac%s' % mozinfo.bits
                self.suffix = 'dmg'
            elif mozinfo.isWin:
                self._platform = 'win32'
                self.suffix = 'zip'
        return self._platform

    def prepare_b2g_desktop(self):
        file_name = self.download_file(lambda x: x.startswith(self.device)
                                        and x.endswith('%s.%s' % (self.platform, self.suffix)))
        mozinstall.install(file_name, self.metadata['workdir'])
        os.remove(file_name)


    def prepare_tests(self):
        self.download_extract(lambda x: x.startswith(self.device) and
                                        x.endswith('%s.tests.zip' % self.platform), outdir='tests')
