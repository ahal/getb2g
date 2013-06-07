import os
import shutil

from ..base import (Base, LeoBase, HamachiBase, InariBase, SymbolsBase)
from ..mixins import TinderboxMixin

import mozfile

__all__ = ['PvtBPvtTinderboxHandler']

class PvtBPvtTinderboxHandler(Base, LeoBase, HamachiBase, InariBase, SymbolsBase, TinderboxMixin):
    """
    Handles resources from pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/tinderbox-builds
    """
    _base_url = 'https://pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/tinderbox-builds/'
    _device_names = { 'inari': 'inari-eng',
                      'leo' : 'leo-eng',
                      'hamachi': 'hamachi-eng' }

    def prepare_symbols(self):
        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('crashreporter-symbols.zip'), outdir='symbols')

    def _prepare_device(self, device):
        self.download_extract(lambda x: x == '%s.zip' % device, outdir=device)
        self.download_extract(lambda x: x == 'gaia.zip')
        self.download_file(lambda x: x == 'build.prop')
        self.download_file(lambda x: x == 'sources.xml')

    def prepare_leo(self):
        self._prepare_device('leo')

    def prepare_hamachi(self):
        self._prepare_device('hamachi')

    def prepare_inari(self):
        self._prepare_device('inari')
