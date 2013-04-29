import os
import shutil
import tempfile

from bs4 import BeautifulSoup
from ..base import (Base, UnagiBase, PandaBase, SymbolsBase)
from ..mixins import TinderboxMixin

import mozfile
__all__ = ['PvtBPubTinderboxHandler']

class PvtBPubTinderboxHandler(Base, UnagiBase, PandaBase, SymbolsBase, TinderboxMixin):
    """
    Handles resources from pvtbuilds.mozilla.org
    """
    _base_url = 'https://pvtbuilds.mozilla.org/pub/mozilla.org/b2g/tinderbox-builds/'
    _device_names = { 'unagi': 'unagi-eng', }

    def prepare_symbols(self):
        url = self.get_resource_url(lambda x: x.startswith('b2g') and
                                                        x.endswith('crashreporter-symbols.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'symbols')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)

    def prepare_panda(self):
        url = self.get_resource_url(lambda x: x == 'boot.tar.bz2')
        file_name = self.download_file(url)
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x == 'system.tar.bz2')
        file_name = self.download_file(url)
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x == 'userdata.tar.bz2')
        file_name = self.download_file(url)
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x == 'gaia-tests.zip')
        test_dir = os.path.join(self.metadata['workdir'], 'tests')
        if os.path.isdir(test_dir):
            shutil.rmtree(test_dir)
        os.makedirs(test_dir)
        file_name = self.download_file(url, 'tests')
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x == 'build.prop')
        self.download_file(url)
        
        url = self.get_resource_url(lambda x: x == 'sources.xml')
        self.download_file(url)

        # license
        doc = self.download_file(self.url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        os.remove(doc)
        text = soup.find_all('pre')[-1].string
        license = open(os.path.join(self.metadata['workdir'], 'license.txt'), 'w')
        license.write(text)
        license.close()

    def prepare_unagi(self):
        url = self.get_resource_url(lambda x: x.startswith('b2g') and
                                                         x.endswith('.tar.gz'))
        file_name = self.download_file(url)
        files = mozfile.extract(file_name)
        os.remove(file_name)
        mvdir = os.path.join(self.metadata['workdir'], 'gecko')
        if os.path.isdir(mvdir):
            shutil.rmtree(mvdir)
        shutil.move(files[0], mvdir)

        url = self.get_resource_url(lambda x: x == 'unagi.zip')
        file_name = self.download_file(url)
        mozfile.extract(file_name)
        os.remove(file_name)

        url = self.get_resource_url(lambda x: x == 'build.prop')
        self.download_file(url)
        
        url = self.get_resource_url(lambda x: x == 'sources.xml')
        self.download_file(url)
