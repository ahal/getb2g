import os
import shutil

from ..base import (Base, LeoBase, HamachiBase, InariBase, OtoroBase, SymbolsBase)
from ..mixins import TinderboxMixin

import mozfile

__all__ = ['PvtBPvtNightlyHandler']

class PvtBPvtNightlyHandler(Base, LeoBase, HamachiBase, InariBase, OtoroBase, SymbolsBase, TinderboxMixin):
    """
    Handles nightly builds from pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/nightly
    """
    _base_url = 'https://pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/nightly'

    @property
    def url(self):
        if self._url:
            return self._url
        if 'build_dir' in self.metadata:
            self._url = self.metadata['build_dir']
            return self._url
        self._url = '%s/%s-%s/latest/' % (self._base_url, self.branch, self.device)
        return self._url

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

    def prepare_otoro(self):
        self._prepare_device('otoro')

        self.download_extract(lambda x: x.startswith('b2g') and
                                        x.endswith('.tar.gz'))
        self.download_file(lambda x: x == 'b2g-gecko-update.mar')
