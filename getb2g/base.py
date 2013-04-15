from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
import inspect
import os
import stat
import sys
import tempfile
import traceback

from mixins.download import DownloadMixin
import mozinfo
import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ('Base', 'GeckoBase', 'SymbolsBase', 'EmulatorBase', 'TestBase', 'valid_resources')
valid_resources = {'all': set([])}


class Base(DownloadMixin):
    __metaclass__ = ABCMeta
    _default_busybox_url = 'http://busybox.net/downloads/binaries/latest/'

    def __init__(self, **kwargs):
        self.data = kwargs

    @classmethod 
    def handled_resources(cls, request):
        """
        Returns a subset of the resources that this class is capable 
        of handling for a specified request
        """
        handled_resources = []
        methods = inspect.getmembers(cls, inspect.ismethod)
        for resource in request.resources:
            for name, ref in methods:
                if name == 'prepare_%s' % resource:
                    handled_resources.append(resource)
        return handled_resources

    @classmethod
    def execute_request(cls, request):
        """
        Executes the specified request
        """
        handled_resources = cls.handled_resources(request)
        for resource in handled_resources:
            success = False
            try:
                h = cls(**request.metadata)
                getattr(h, 'prepare_%s' % resource)()
                request.resources.remove(resource)
            except:
                log.debug(traceback.format_exc())
    
    def prepare_busybox(self):
        """
        Downloads a busybox binary for the given platform
        """
        url = self._default_busybox_url
        platform = self.data.get('busybox_platform') or self.data.get('platform', 'armv6l')

        doc = self.download_file(url, tempfile.mkstemp()[1])
        soup = BeautifulSoup(open(doc, 'r'))
        for link in soup.find_all('a'):
            if 'busybox-%s' % platform in link['href']:
                path = os.path.join(self.data['workdir'], 'busybox')
                if os.path.isfile(path):
                    os.remove(path)
                file_name = self.download_file(url + link['href'], 'busybox')
                os.chmod(file_name, stat.S_IEXEC)
                break
        else:
            log.error("Couldn't find a busybox binary for platform '%s'" % platform)

class GeckoBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_gecko(self):
        """
        Downloads and extracts a gecko directory
        for the given args
        """

class SymbolsBase(object):
    __metaclass__ = ABCMeta
    _default_minidump_stackwalk_url = 'https://hg.mozilla.org/build/tools/file/tip/breakpad/%s/minidump_stackwalk'

    @abstractmethod
    def prepare_symbols(self):
        """
        Returns the path to an unzipped symbols directory
        for the given args
        """

    def prepare_minidump_stackwalk(self, url=None):
        """
        Downloads the minidump stackwalk binaries if missing
        """
        if not url:
            arch = '64' if mozinfo.bits == 64 else ''
            if mozinfo.isLinux:
                url = self._default_minidump_stackwalk_url % ('linux%s' % arch)
            elif mozinfo.isMac:
                url = self._default_minidump_stackwalk_url % ('osx%s' % arch)
            elif mozinfo.isWin:
                url = self._default_minidump_stackwalk_url % 'win32'
        file_name = self.download_file(url, 'minidump_stackwalk')
        os.chmod(file_name, stat.S_IEXEC)

class TestBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_tests(self):
        """
        Returns the path to an unzipped tests bundle
        """

class EmulatorBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_emulator(self):
        """
        Returns the path to an unzipped emulator package
        """
    prepare_emulator.groups = ['device']

class UnagiBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_unagi(self):
        """
        Returns the path to an extracted unagi build 
        """
    prepare_unagi.groups = ['device']

class OtoroBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_otoro(self):
        """
        Returns the path to an extracted otoro build 
        """
    prepare_otoro.groups = ['device']

# inspect the abstract base classes and extract the valid resources
for cls_name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    for name, method in inspect.getmembers(cls, inspect.ismethod):
        if name.startswith('prepare'):
            name = name[len('prepare_'):].lower() 
            valid_resources['all'].add(name)
            for group in getattr(method, 'groups', []):
                if group not in valid_resources:
                    valid_resources[group] = set([])
                valid_resources[group].add(name)
