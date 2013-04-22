import os
import shutil

from ..base import (Base, EmulatorBase)
from ..mixins import DateMixin

import mozfile

__all__ = ['ReleaseMOHandler']


class ReleaseMOHandler(Base, EmulatorBase, DateMixin):
    """
    Handles resources from releases.mozilla.com
    """
    _base_url = 'https://releases.mozilla.com/b2g'

    def prepare_emulator(self):
        url = '%s/%s/' % (self._base_url, '%s')
        url = self.get_date_url(url, lambda x: x.string.startswith('emulator-arm')
                                                        and x.string.endswith('zip'))
        file_name = self.download_file(url, 'emulator.zip')
        extract_dir = os.path.join(self.metadata['workdir'], 'b2g-distro')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name)
        os.remove(file_name)
