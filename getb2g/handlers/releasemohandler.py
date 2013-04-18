import os
import shutil
import tempfile

from bs4 import BeautifulSoup
from ..base import (Base, EmulatorBase)

import mozfile
import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ['ReleaseMOHandler']

class Date(object):
    def __init__(self, year, month, day, format_char='-'):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.format_char = format_char

    def __cmp__(self, other):
        for a in ['year', 'month', 'day']:
            if getattr(self, a) > getattr(other, a):
                return 1
            elif getattr(self, a) < getattr(other, a):
                return -1
        return 0
            
    def __str__(self):
        return "%s%s%s%s%s" % (self.year, self.format_char, str(self.month).zfill(2),
                                self.format_char, str(self.day).zfill(2))

class ReleaseMOHandler(Base, EmulatorBase):
    """
    Handles resources from releases.mozilla.com
    """
    _default_releases_url = 'https://releases.mozilla.com/b2g/'

    def __init__(self, **kwargs):
        super(ReleaseMOHandler, self).__init__(**kwargs)
        self.date = self.metadata.get('date', 'latest')


    def _get_date_from_string(self, string, format_char='-'):
        tokens = string.rstrip('/').split(format_char)
        if len(tokens) < 3:
            return
        for tok in tokens:
            try:
                int(tok)
            except ValueError:
                break
        else:
            return Date(*tokens, format_char=format_char)

    def _get_next_latest_date(self, prev_date):
        doc = self.download_file(self._default_releases_url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        prev_date = self._get_date_from_string(prev_date)
        if not prev_date:
            prev_date = Date(9999,0,0)

        next_date = Date(0, 0, 0)
        for link in soup.find_all('a'):
            date = self._get_date_from_string(link.string) 
            if not date:
                continue
            if date < prev_date and date > next_date:
                next_date = date

        return str(next_date)

    def _get_resource_url(self, date, condition):
        url = self._default_releases_url + date.rstrip('/') + '/'
        doc = self.download_file(url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        os.remove(doc)
        for link in soup.find_all('a'):
            if condition(link):
                return url + link.string

    def prepare_emulator(self, date=None):
        date = date or self.date
        url = self._get_resource_url(date, lambda x: x.string.startswith('emulator-arm') and
                                                        x.string.endswith('zip'))
        if date == 'latest' and not url:
            for i in range(0, 10):
                log.warning("No emulator build found for date '%s', trying an earlier date" % date)
                date = self._get_next_latest_date(date)
                url = self._get_resource_url(date, lambda x: x.string.startswith('emulator-arm') and
                                                        x.string.endswith('zip'))
                if url:
                    break
            else:
                #TODO raise
                log.warning("Failed to find a recent emulator build on releases.mozilla.com")
        elif not url:
            #TODO raise
            log.warning("Failed to find an emulator build for date '%s'" % date)
            
        file_name = self.download_file(url, 'emulator.zip')
        files = mozfile.extract(file_name)
        os.remove(file_name)
        extract_dir = os.path.join(self.metadata['workdir'], 'emulator')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        shutil.move(files[0], extract_dir)
