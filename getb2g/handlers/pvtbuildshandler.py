import os
import shutil
import tempfile

from bs4 import BeautifulSoup
from ..base import (Base, UnagiBase, PandaBase, SymbolsBase)
from ..mixins import TinderboxMixin

import mozfile
__all__ = ['PvtbuildsHandler']

class PvtbuildsHandler(Base, UnagiBase, PandaBase, SymbolsBase, TinderboxMixin):
    """
    Handles resources from pvtbuilds.mozilla.org
    """
    _base_url = 'https://pvtbuilds.mozilla.org/pub/mozilla.org/b2g/tinderbox-builds/'
    _device_names = { 'panda': 'panda',
                      'unagi': 'unagi-eng' }

    def prepare_symbols(self):
        url = self.get_resource_url(lambda x: x.string.startswith('b2g') and
                                                        x.string.endswith('crashreporter-symbols.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'symbols')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)

    def prepare_panda(self):
        panda_dir = os.path.join(self.metadata['workdir'], 'panda')
        if os.path.isdir(panda_dir):
            shutil.rmtree(panda_dir)
        os.makedirs(panda_dir)

        url = self.get_resource_url(lambda x: x.string == 'boot.tar.bz2')
        file_name = self.download_file(url, 'panda')
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x.string == 'system.tar.bz2')
        file_name = self.download_file(url, 'panda')
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x.string == 'userdata.tar.bz2')
        file_name = self.download_file(url, 'panda')
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x.string == 'gaia-tests.zip')
        file_name = self.download_file(url, 'panda')
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x.string == 'build.prop')
        self.download_file(url, 'panda')
        
        url = self.get_resource_url(lambda x: x.string == 'sources.xml')
        self.download_file(url, 'panda')

        # license
        doc = self.download_file(self.url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        text = soup.find_all('pre')[-1].string
        license = open(os.path.join(self.metadata['workdir'], 'panda', 'license.txt'), 'w')
        license.write(text)
        license.close()

    def prepare_unagi(self):
        unagi_dir = os.path.join(self.metadata['workdir'], 'unagi')
        if os.path.isdir(unagi_dir):
            shutil.rmtree(unagi_dir)
        os.makedirs(unagi_dir)

        url = self.get_resource_url(lambda x: x.string.startswith('b2g') and
                                                         x.string.endswith('.tar.gz'))
        file_name = self.download_file(url, 'unagi')
        files = mozfile.extract(file_name)
        os.remove(file_name)
        mvdir = os.path.join(self.metadata['workdir'], 'gecko')
        if os.path.isdir(mvdir):
            shutil.rmtree(mvdir)
        shutil.move(files[0], mvdir)

        url = self.get_resource_url(lambda x: x.string == 'unagi.zip')
        file_name = self.download_file(url, 'unagi')
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x.string == 'build.prop')
        self.download_file(url, 'unagi')
        
        url = self.get_resource_url(lambda x: x.string == 'sources.xml')
        self.download_file(url, 'unagi')
