import os
import shutil

from ..base import (Base, GeckoBase, SymbolsBase, TestBase)
from ..mixins import TinderboxMixin

import mozfile

__all__ = ['FtpTinderboxHandler']

class FtpTinderboxHandler(Base, GeckoBase, SymbolsBase, TestBase, TinderboxMixin):
    """
    Handles resources from uploaded tinderbox builds
    """
    _base_url = 'http://ftp-scl3.mozilla.com/pub/mozilla.org/b2g/tinderbox-builds/'
    _device_names = { 'emulator': 'ics_armv7a_gecko' }

    def prepare_gecko(self):
        url = self.get_resource_url(lambda x: x.startswith('b2g') and
                                                         x.endswith('.tar.gz'))
        file_name = self.download_file(url)
        files = mozfile.extract(file_name)
        os.remove(file_name)
        extract_dir = os.path.join(self.metadata['workdir'], 'gecko')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        shutil.move(files[0], extract_dir)

    def prepare_tests(self):
        url = self.get_resource_url(lambda x: x.startswith('b2g') and
                                                        x.endswith('tests.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'tests')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)

    def prepare_symbols(self):
        url = self.get_resource_url(lambda x: x.startswith('b2g') and
                                                        x.endswith('crashreporter-symbols.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'symbols')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)

