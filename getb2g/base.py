from abc import ABCMeta, abstractmethod
import mozfile

__all__ = ('Base', 'GeckoBase', 'SymbolsBase', 'EmulatorBase', 'TestBase')

class Base(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def handles_request(self, request):
        """
        Returns true if the class is capable of handling the specified request
        """

    @abstractmethod
    def prompt_story(self):
        """
        Prompts the user to provide any additional missing information
        """
    

class GeckoBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_gecko(self, *args, **kwargs):
        """
        Returns path to an unzipped gecko directory
        for the given revision
        """

class SymbolsBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_symbols(self, *args, **kwargs):
        """
        Returns the path to an unzipped symbols directory
        for the given revision
        """

    def prepare_minidump_stackwalk(self):
        """
        Downloads the minidump stackwalk binaries if missing
        """

class EmulatorBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_emulator(self, *args, **kwargs):
        """
        Returns the path to an unzipped emulator package
        """
    
    def prepare_busybox(self, platform):
        """
        Returns the path of a busybox binary for the given platform
        """

class TestBase(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def prepare_tests(self, *args, **kwargs):
        """
        Returns the path to an unzipped tests bundle
        """
