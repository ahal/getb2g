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
        url = self.get_resource_url(lambda x: x.startswith('b2g') and
                                                        x.endswith('crashreporter-symbols.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'symbols')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)

    def _prepare_device(self, device):
        url = self.get_resource_url(lambda x: x == '%s.zip' % device)
        file_name = self.download_file(url)
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x == 'build.prop')
        self.download_file(url)

        url = self.get_resource_url(lambda x: x == 'sources.xml')
        self.download_file(url)

    def prepare_leo(self):
        self._prepare_device('leo')

    def prepare_hamachi(self):
        self._prepare_device('hamachi')

    def prepare_inari(self):
        self._prepare_device('inari')
