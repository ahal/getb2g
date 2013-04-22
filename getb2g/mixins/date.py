import os
import tempfile
import urllib2

from bs4 import BeautifulSoup
from ..errors import PrepareFailedException

import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ['DateMixin']

class Date(object):
    format_char = '-'
    def __init__(self, *tokens):
        self.tokens = [int(t) for t in tokens]

    def __cmp__(self, other):
        for i, this in enumerate(self.tokens):
            if i < len(other.tokens):
                if this > other.tokens[i]:
                    return 1
                elif this < other.tokens[i]:
                    return -1
        return 0

    def __str__(self):
        return self.format_char.join([str(s).zfill(2) for s in self.tokens])

class DateMixin(object):
    _date = None

    @property
    def date(self):
        if not self._date:
            self._date = self.metadata.get('date', 'latest')
        return self._date

    def _get_resource_url(self, url, condition=None):
        try:
            doc = self.download_file(url, tempfile.mkstemp()[1], silent=True)
        except urllib2.HTTPError:
            return
        if condition:
            soup = BeautifulSoup(open(doc, 'r'))
            for link in soup.find_all('a'):
                if condition(link):
                    return url + link.string
        else:
            return url

    def _get_date_from_string(self, string, format_char='-'):
        t = []
        tokens = string.rstrip('/').split(format_char)
        for tok in tokens:
            try:
                int(tok)
                t.append(tok)
            except ValueError:
                break
        if len(t) < 3:
            return
        return Date(*t)

    def _get_next_latest_date(self, prev_date):
        doc = self.download_file(self._base_url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        prev_date = self._get_date_from_string(prev_date)
        if not prev_date:
            prev_date = Date(9999,0,0,0,0,0)

        next_date = Date(0,0,0,0,0,0)
        for link in soup.find_all('a'):
            date = self._get_date_from_string(link.string)
            if not date:
                continue
            if date < prev_date and date > next_date:
                next_date = date
        return str(next_date)

    def get_date_url(self, sub_url, condition=None):
        url = self._get_resource_url(sub_url % self.date, condition)
        if self.date == 'latest' and not url:
            for i in range(0, 7):
                log.warning("No resource found for date '%s', trying an earlier date" % self.date)
                self._date = self._get_next_latest_date(self.date)
                url = self._get_resource_url(sub_url % self.date, condition)
                if url:
                    break
            else:
                log.warning("Failed to find a recent emulator build on '%s'" % self._base_url)
                raise PrepareFailedException()
        elif not url:
            log.warning("Failed to find resource for date '%s'" % self.date)
            raise PrepareFailedException()
        return url


