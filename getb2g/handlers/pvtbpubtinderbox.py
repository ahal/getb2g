import os
import shutil
import tempfile

from bs4 import BeautifulSoup
from ..base import (Base, EmulatorBase, UnagiBase, PandaBase, SymbolsBase, TestBase)
from ..mixins import TinderboxMixin

import mozfile
__all__ = ['PvtBPubTinderboxHandler']

class PvtBPubTinderboxHandler(Base, EmulatorBase, UnagiBase, PandaBase, SymbolsBase, TestBase, TinderboxMixin):
    """
    Handles resources from pvtbuilds.mozilla.org
    """
    _base_url = 'https://pvtbuilds.mozilla.org/pub/mozilla.org/b2g/tinderbox-builds/'
    _device_names = { 'unagi': 'unagi-eng',
                      'emulator': 'generic', }

    def prepare_tests(self):
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('tests.zip'), outdir='tests')

    def prepare_symbols(self):
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('crashreporter-symbols.zip'), outdir='symbols')

    def prepare_panda(self):
        self.download_extract(lambda x: x == 'boot.tar.bz2')
        self.download_extract(lambda x: x == 'system.tar.bz2')
        self.download_extract(lambda x: x == 'userdata.tar.bz2')
        self.download_extract(lambda x: x == 'gaia.zip')
        self.download_extract(lambda x: x == 'gaia-tests.zip')
        self.download_file(lambda x: x == 'build.prop')
        self.download_file(lambda x: x == 'sources.xml')

        # license
        doc = self.download_file(self.url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        os.remove(doc)
        text = soup.find_all('pre')[-1].string
        license = open(os.path.join(self.metadata['workdir'], 'license.txt'), 'w')
        license.write(text)
        license.close()

    def prepare_unagi(self):
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('.tar.gz'), outdir='b2g')
        self.download_extract(lambda x: x == 'unagi.zip', outdir='unagi')
        self.download_file(lambda x: x == 'build.prop')
        self.download_file(lambda x: x == 'sources.xml')

    def prepare_emulator(self):
        self.download_extract(lambda x: x == 'emulator.tar.gz', outdir='emulator')
        self.download_extract(lambda x: x == 'gaia.zip')
        self.download_file(lambda x: x == 'sources.xml')
        self.download_file(lambda x: x == 'build.prop')
