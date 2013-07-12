from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
import inspect
import os
import shutil
import stat
import sys
import tempfile
import traceback

from mixins import DownloadMixin, StorageMixin
import mozfile
import mozinfo
import mozlog
log = mozlog.getLogger('GetB2G')

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
                parents = get_parent_resources(res)
                if all(p not in request.resources for p in parents) \
                        or any('prepare_%s' % p in methods for p in parents) \
                        or res in valid_resources['device']:
                    handled_resources.append(res)
        return handled_resources

    @classmethod
    def execute_request(cls, request):
        """
        Executes the specified request
        """
        handled_resources = cls.handled_resources(request)
        for resource in handled_resources:
            log.info("preparing '%s'" % resource)
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
                break

    def prepare_busybox(self):
        """
        Prepares the busybox binary
        """
        url = self._default_busybox_url
        platform = self.metadata.get('busybox_platform', 'armv6l')

        doc = self.download_file(url, tempfile.mkstemp()[1], silent=True)
        soup = BeautifulSoup(open(doc, 'r'))
        os.remove(doc)
        for link in soup.find_all('a'):
            if 'busybox-%s' % platform in link['href']:
                path = os.path.join(self.metadata['workdir'], 'busybox')
                if os.path.isfile(path):
                    os.remove(path)
                file_name = self.download_file(url + link['href'], 'busybox')
                os.chmod(file_name, stat.S_IEXEC | stat.S_IREAD)
                break
        else:
            log.error("Couldn't find a busybox binary for platform '%s'" % platform)
    prepare_busybox.groups = ['default']

class SymbolsBase(object):
    __metaclass__ = ABCMeta
    _default_minidump_stackwalk_url = 'https://hg.mozilla.org/build/tools/file/tip/breakpad/%s/minidump_stackwalk'

    @abstractmethod
    def prepare_symbols(self):
        """
        Prepares the symbols directory
        """
    prepare_symbols.groups = ['unagi', 'panda', 'leo', 'hamachi', 'inari', 'otoro']

    def prepare_minidump_stackwalk(self, url=None):
        """
        Prepares the minidump stackwalk binary
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
        os.chmod(file_name, stat.S_IEXEC | stat.S_IREAD)
    prepare_minidump_stackwalk.groups = ['symbols']

class TestBase(object):
    __metaclass__ = ABCMeta
    _default_xre_url = 'http://people.mozilla.com/~ahalberstadt/getb2g/xre.zip'

    @abstractmethod
    def prepare_tests(self):
        """
        Prepares the tests bundle
        """
    prepare_tests.groups = ['emulator', 'b2g_desktop', 'panda']

    def prepare_xre(self, url=None):
        """
        Prepares the xre directory
        """
        url = url or self._default_xre_url
        file_name = self.download_file(url)
        path = os.path.join(self.metadata['workdir'], 'xre')
        if os.path.isdir(path):
            shutil.rmtree(path)
        files = mozfile.extract(file_name)
        os.remove(file_name)
    prepare_xre.groups = ['tests']

class EmulatorBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_emulator(self):
        """
        Prepares the emulator package
        """
    prepare_emulator.groups = ['device', 'cli']

class UnagiBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_unagi(self):
        """
        Prepares the unagi build
        """
    prepare_unagi.groups = ['device', 'cli']

class PandaBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_panda(self):
        """
        Prepares the panda build
        """
    prepare_panda.groups = ['device', 'cli']

class B2GDesktopBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_b2g_desktop(self):
        """
        Prepares the b2g desktop build
        """
    prepare_b2g_desktop.groups = ['device', 'cli']

class LeoBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_leo(self):
        """
        Prepares the leo build
        """
    prepare_leo.groups = ['device', 'cli']

class HamachiBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_hamachi(self):
        """
        Prepares the hamachi build
        """
    prepare_hamachi.groups = ['device', 'cli']

class InariBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_inari(self):
        """
        Prepares the inari build
        """
    prepare_inari.groups = ['device', 'cli']

class OtoroBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_otoro(self):
        """
        Prepares the otoro build
        """
    prepare_otoro.groups = ['device', 'cli']

def get_parent_resources(resource):
    parents = []
    for res in valid_resources['all']:
        if res in valid_resources:
            if resource in valid_resources[res]:
                parents.append(res)
    return parents

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
