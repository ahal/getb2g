from abc import ABCMeta, abstractmethod
import getpass
import inspect
import traceback
import sys

import mozinfo

__all__ = ('Base', 'GeckoBase', 'SymbolsBase', 'EmulatorBase', 'TestBase', 'valid_resources')

valid_resources = {'all': set([])}


class Base(object):
    __metaclass__ = ABCMeta

    def prompt_story(self, data=None):
        """
        Prompts the user to provide any additional missing information
        """
        data = data or self.__dict__

        # username and password
        if data.username and not data.password:
            print "No password found for user '%s'!" % data.username
            options = {'1': 'Enter password',
                       '2': 'Ignore username'}
            while True:
                print ['[%s] %s\n' % (k, v) for k, v in options.iteritems()]
                option = raw_input("$ ")
                if option in options.keys():
                    break
            if option == options.keys()[0]:
                data.password = getpass.getpass()
            elif option == options.keys()[1]:
                data.username = None
        return data
                

    @classmethod 
    def handled_resources(cls, request):
        """
        Returns a subset of the resources that this class is capable 
        of handling for a specified request
        """
        # A resource can be handled iff
        # 1. the handler contains a callee named 'prepare_resource'
        # 2. the specified args all exist in the callee
        # 3. all args in the callee without a default exist in the specified args
        handled_resources = []
        methods = inspect.getmembers(cls, inspect.ismethod)
        for resource, kwargs in request.resources:
            for name, ref in methods:
                if name == 'prepare_%s' % resource:
                    if set(kwargs.keys()).issubset(set(inspect.getargspec(ref)[0])):
                        handled_resources.append((resource, kwargs))
        return handled_resources

    @classmethod
    def execute_request(cls, request):
        """
        Executes the specified request
        """
        handled_resources = cls.handled_resources(request)
        for resource, kwargs in handled_resources:
            success = False
            try:
                h = cls(**request.state)
                success = getattr(h, 'prepare_%s' % resource)(**kwargs)
            except:
                traceback.print_exc()
            if success:
                request.resources.remove((resource, kwargs))
    
    def prepare_busybox(self, platform):
        """
        Returns the path of a busybox binary for the given platform
        """


class GeckoBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_gecko(self, *args, **kwargs):
        """
        Returns path to an unzipped gecko directory
        for the given args
        """

class SymbolsBase(object):
    __metaclass__ = ABCMeta
    _default_minidump_stackwalk_url = 'https://hg.mozilla.org/build/tools/file/tip/breakpad/%s/minidump_stackwalk'

    @abstractmethod
    def prepare_symbols(self, *args, **kwargs):
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
        self.download_file(url, 'minidump_stackwalk')
                
class TestBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_tests(self, *args, **kwargs):
        """
        Returns the path to an unzipped tests bundle
        """

class EmulatorBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_emulator(self, *args, **kwargs):
        """
        Returns the path to an unzipped emulator package
        """
    prepare_emulator.groups = ['device']

class UnagiBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_unagi(self, *args, **kwargs):
        """
        Returns the path to an extracted unagi build 
        """
    prepare_unagi.groups = ['device']

class OtoroBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_otoro(self, *args, **kwargs):
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
print "valid_resources: %s" % valid_resources['all']
