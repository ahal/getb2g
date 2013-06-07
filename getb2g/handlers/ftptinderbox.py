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
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('.tar.gz'), outdir='gecko')

    def prepare_tests(self):
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('tests.zip'), outdir='tests')

    def prepare_symbols(self):
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('crashreporter-symbols.zip'), outdir='symbols')
