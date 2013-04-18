import tempfile

from bs4 import BeautifulSoup
from ..prompt import prompt

__all__ = ('TinderboxMixin',)

class TinderboxMixin(object):
    _base_url = None
    _branch = None
    _url = None
    _device = None
    _device_names = None
    
    @property
    def branch(self):
        if self._branch:
            return self._branch
        branches = self.get_available_branches()
        self._branch = self.metadata.get('branch')
        if not self._branch or self._branch not in branches:
            self._branch = prompt('Which branch would you like to use?', branches)
        if not self._branch:
            self._branch = [b for b in ['mozilla-central', 'mozilla-b2g18'] if b in branches][0]
        self.metadata['branch'] = self._branch
        return self._branch

    @property
    def url(self):
        if self._url:
            return self._url
        url = self._base_url + '%s-%s' % (self.branch, self.device)
        doc = self.download_file(url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))

        identifier = 0
        for tr in soup.find_all('tr')[3:-1]:
            temp = int(tr.find_all('a')[0].string.rstrip('/'))
            if temp > identifier:
                identifier = temp
        self._url = url.rstrip('/') + '/%s/' % identifier
        return self._url

    @property
    def device(self):
        if self._device:
            return self._device
        self._device = self._device_names.get(self.metadata.get('device', '')) or self._device_names.values()[0]
        return self._device
    
    def get_resource_url(self, condition):
        doc = self.download_file(self.url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        for link in soup.find_all('a'):
            if condition(link):
                return self.url + link.string

    def get_available_branches(self):
        doc = self.download_file(self._base_url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        branches = set([])
        for tr in soup.find_all('tr')[3:-1]:
            s = tr.find_all('a')[0].string.rstrip('/')
            if s.endswith(self.device):
                branches.add(s[:-(len(self.device)+1)])
        return sorted(list(branches))
