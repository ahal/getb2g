import os
import shutil

from ..base import (Base, EmulatorBase)
from ..mixins import DateMixin
from ..prompt import prompt

import mozfile

__all__ = ['ReleasesHandler']


class ReleasesHandler(Base, EmulatorBase, DateMixin):
    """
    Handles resources from releases.mozilla.com
    """
    _base_url = 'https://releases.mozilla.com/b2g'
    _base_branch = 'mozilla-b2g18'

    def prepare_emulator(self):
        if self.metadata.get('branch', self._base_branch) != self._base_branch:
            q = "The emulators on releases.mozilla.org are based on %s, but you specified '%s'. Do want to switch to %s instead?"
            if prompt(q % (self._base_branch, self.metadata['branch'], self._base_branch)) == 'y':
                self.metadata['branch'] = self._base_branch
        else:
            self.metadata['branch'] = self._base_branch

        url = '%s/%s/' % (self._base_url, '%s')
        url = self.get_date_url(url, lambda x: x.string.startswith('emulator-arm')
                                                        and x.string.endswith('tar.gz'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(self.metadata['workdir'], 'b2g-distro')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name)
        os.remove(file_name)
