import os
import shutil

from ..base import (Base, UnagiBase, SymbolsBase)
from ..mixins import TinderboxMixin

import mozfile

__all__ = ['PvtBPubNightlyHandler']

class PvtBPubNightlyHandler(Base, UnagiBase, SymbolsBase, TinderboxMixin):
    """
    Handles nightly builds from pvtbuilds.mozilla.org/pub/mozilla.org/b2g/nightly
    """
    _base_url = 'https://pvtbuilds.mozilla.org/pub/mozilla.org/b2g/nightly'

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

    def prepare_unagi(self):
        self.download_extract(lambda x: x == 'unagi.zip', outdir='unagi')
        self.download_extract(lambda x: x == 'gaia.zip')
        self.download_file(lambda x: x == 'build.prop')
        self.download_file(lambda x: x == 'sources.xml')
        self.download_file(lambda x: x == 'b2g-gecko-update.mar')
