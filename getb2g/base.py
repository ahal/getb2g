from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
import inspect
import os
import stat
import sys
import tempfile
import traceback

from mixins import DownloadMixin, StorageMixin
import mozinfo
import mozlog
log = mozlog.getLogger('GetB2G')

__all__ = ('Base', 'GeckoBase', 'SymbolsBase', 'EmulatorBase', 'TestBase', 'valid_resources')

class Base(DownloadMixin, StorageMixin):
    __metaclass__ = ABCMeta
    _default_busybox_url = 'http://busybox.net/downloads/binaries/latest/'

    def __init__(self, **metadata):
        self.metadata = metadata
        super(Base, self).__init__()

    @classmethod
    def handled_resources(cls, request):
        """
        Returns a subset of the resources that this class is capable
        of handling for a specified request
        """
        handled_resources = []
        methods = [name for name, ref in inspect.getmembers(cls, inspect.ismethod)]
        
        for res in request.resources:
            if 'prepare_%s' % res in methods:
                if res in valid_resources:
                    if all(r not in request.resources for r in valid_resources[res]) or any('prepare_%s' % r in methods for r in valid_resources[res]):
                        handled_resources.append(res)
                else:
                    handled_resources.append(res)
        return handled_resources

    @classmethod
    def execute_request(cls, request):
        """
        Executes the specified request
        """
        handled_resources = cls.handled_resources(request)
        for resource in handled_resources:
            log.info("Preparing '%s'" % resource)
            try:
                h = cls(**request.metadata)
                getattr(h, 'prepare_%s' % resource)()
                request.metadata = h.metadata
                request.resources.remove(resource)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                log.warning("%s encountered an error while attempting to prepare '%s'" % (cls.__name__, resource))
                log.debug(traceback.format_exc())

    def prepare_busybox(self):
        """
        Downloads a busybox binary for the given platform
        """
        url = self._default_busybox_url
        platform = self.metadata.get('busybox_platform') or self.metadata.get('platform', 'armv6l')

        doc = self.download_file(url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        for link in soup.find_all('a'):
            if 'busybox-%s' % platform in link['href']:
                path = os.path.join(self.metadata['workdir'], 'busybox')
                if os.path.isfile(path):
                    os.remove(path)
                file_name = self.download_file(url + link['href'], 'busybox')
                os.chmod(file_name, stat.S_IEXEC)
                break
        else:
            log.error("Couldn't find a busybox binary for platform '%s'" % platform)
    prepare_busybox.groups = ['default']

class GeckoBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_gecko(self):
        """
        Downloads and extracts a gecko directory
        for the given args
        """
    prepare_gecko.groups = ['emulator']

class SymbolsBase(object):
    __metaclass__ = ABCMeta
    _default_minidump_stackwalk_url = 'https://hg.mozilla.org/build/tools/file/tip/breakpad/%s/minidump_stackwalk'

    @abstractmethod
    def prepare_symbols(self):
        """
        Returns the path to an unzipped symbols directory
        for the given args
        """
    prepare_symbols.groups = ['gecko', 'unagi', 'panda']

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
        path = os.path.join(self.metadata['workdir'], 'minidump_stackwalk')
        if os.path.isfile(path):
            os.remove(path)
        file_name = self.download_file(url, 'minidump_stackwalk')
        os.chmod(file_name, stat.S_IEXEC)
    prepare_minidump_stackwalk.groups = ['symbols']

class TestBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_tests(self):
        """
        Returns the path to an unzipped tests bundle
        """
    prepare_tests.groups = ['gecko']

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

class PandaBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_panda(self):
        """
        Returns the path to an extracted panda build
        """
    prepare_panda.groups = ['device']

# inspect the abstract base classes and extract the valid resources
valid_resources = {'all': set([])}
for cls_name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    for name, method in inspect.getmembers(cls, inspect.ismethod):
        if name.startswith('prepare'):
            name = name[len('prepare_'):].lower()
            valid_resources['all'].add(name)
            for group in getattr(method, 'groups', []):
                if group not in valid_resources:
                    valid_resources[group] = set([])
                valid_resources[group].add(name)
