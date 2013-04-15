import os
import shutil
import sys
import tempfile

from bs4 import BeautifulSoup
from base import (Base, EmulatorBase, GeckoBase, SymbolsBase, TestBase)

import mozfile
import mozinfo
import mozlog

__all__ = ['all_handlers']

all_handlers = ['TinderboxHandler', 'PvtbuildsHandler', 'ReleaseMOHandler']
__all__.extend(all_handlers)

class TinderboxHandler(Base, GeckoBase, SymbolsBase, TestBase):
    """
    Handles resources from uploaded tinderbox builds
    """
    _base_url = 'http://ftp-scl3.mozilla.com/pub/mozilla.org/b2g/tinderbox-builds/'
    _branch = None
    _url = None

    @property
    def branch(self):
        if self._branch:
            return self._branch
        # TODO prompt for branch
        self._branch = 'mozilla-central'
        return self._branch

    @property
    def url(self):
        if self._url:
            return self._url
        url = self._base_url + '%s-ics_armv7a_gecko' % self.branch
        doc = self.download_file(url, tempfile.mkstemp()[1])
        soup = BeautifulSoup(open(doc, 'r'))

        identifier = 0
        for tr in soup.find_all('tr')[3:-1]:
            temp = int(tr.find_all('a')[0].string.rstrip('/'))
            if temp > identifier:
                identifier = temp
        self._url = url.rstrip('/') + '/%s/' % identifier
        return self._url

    def _get_resource_url(self, url, condition):
        doc = self.download_file(url, tempfile.mkstemp()[1])
        soup = BeautifulSoup(open(doc, 'r'))
        for link in soup.find_all('a'):
            if condition(link):
                return url + link.string

    def prepare_gecko(self, url=None):
        url = url or self.url
        url = self._get_resource_url(url, lambda x: x.string.startswith('b2g') and
                                                         x.string.endswith('.tar.gz'))
        file_name = self.download_file(url)
        files = mozfile.extract(file_name)
        os.remove(file_name)
        extract_dir = os.path.join(self.data['workdir'], 'gecko')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        shutil.move(files[0], extract_dir)


    def prepare_tests(self, url=None):
        url = url or self.url
        url = self._get_resource_url(url, lambda x: x.string.startswith('b2g') and
                                                        x.string.endswith('tests.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'tests')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)

    def prepare_symbols(self, url=None):
        url = url or self.url
        url = self._get_resource_url(url, lambda x: x.string.startswith('b2g') and
                                                        x.string.endswith('crashreporter-symbols.zip'))
        file_name = self.download_file(url)
        extract_dir = os.path.join(os.path.dirname(file_name), 'symbols')
        if os.path.isdir(extract_dir):
            shutil.rmtree(extract_dir)
        mozfile.extract(file_name, extract_dir)
        os.remove(file_name)


class PvtbuildsHandler(Base):
    """
    Handles resources from pvtbuilds.mozilla.org
    """

class ReleaseMOHandler(Base, EmulatorBase):
    """
    Handles resources from releases.mozilla.com
    """
    _default_releases_url = 'https://releases.mozilla.com/b2g/'

    def __init__(self, **kwargs):
        super(ReleaseMOHandler, self).__init__(**kwargs)
        self.date = self.data.get('date', 'latest')

    class Date(object):
        def __init__(self, year, month, day, format_char='-'):
            self.year = int(year)
            self.month = int(month)
            self.day = int(day)
            self.format_char = format_char

        def __cmp__(self, other):
            if self.year > other.year:
                return 1
            if self.month > other.month:
                return 1
            if self.day > other.day:
                return 1
            if self.year == other.year and self.month == other.month and self.day == other.day:
                return 0
            return -1
                
        def __str__(self):
            return "%s%s%s%s%s" % (self.year, self.format_char, self.month,
                                    self.format_char, self.day)


    def _get_date_from_string(self, string, format_char='-'):
        tokens = string.rstrip('/').split(format_char)
        for tok in tokens:
            try:
                int(tok)
            except ValueError:
                break
        else:
            return Date(*tokens, format_char=format_char)

    def _get_next_latest_date(self, prev_date):
        doc = self.download_file(self._default_releases_url, tempfile.mkstemp()[0])
        soup = BeautifulSoup(open(doc, 'r'))
        prev_date = self._get_date_from_string(prev_date)
        next_date = Date(0, 0, 0)

        if not prev_date:
            # TODO raise
            pass

        for link in soup.find_all('a'):
            date = self._get_date_from_string(link.string) 
            if date < prev_date and date > next_date:
                next_date = date
        return str(next_date)

    def _get_resource_url(self, date, condition):
        url = self._default_releases_url + date.rstrip('/') + '/'
        doc = self.download_file(url, tempfile.mkstemp()[1])
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
                log.warning("No emulator build found for date '%s', trying an earlier date")
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
        else:
            file_name = self.download_file(url, 'emulator.zip')
            files = mozfile.extract(file_name)
            os.remove(file_name)
            extract_dir = os.path.join(self.data['workdir'], 'emulator')
            print files[0]
            print extract_dir
            if os.path.isdir(extract_dir):
                shutil.rmtree(extract_dir)
            shutil.move(files[0], extract_dir)
