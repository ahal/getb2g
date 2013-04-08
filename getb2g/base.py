from abc import ABCMeta, abstractmethod
import inspect
import traceback

__all__ = ('Base', 'GeckoBase', 'SymbolsBase', 'EmulatorBase', 'TestBase')

class Base(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def prompt_story(self):
        """
        Prompts the user to provide any additional missing information
        """

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
        for resource, args, kwargs in request.resources:
            for name, ref in methods:
                if name == 'prepare_%s' % resource:
                    t_args = args
                    t_args.extend(kwargs.keys())
                    ins_args = inspect.getargspec(ref)
                    if set(t_args).issubset(set(ins_args[0])) and
                            set(ins_args[0][:len(ins_args[3] or len(ins_args[0])]).issubset(set(t_args)):
                        handled_resources.append((resource, args, kwargs))
        return handled_resources

    @classmethod
    def execute_request(cls, request):
        """
        Executes the specified request
        """
        handled_resources = cls.handled_resources(request)
        for resource, args, kwargs in handled_resources:
            success = False
            try:
                h = cls.__class__(**request.state)
                success = getattr(h, 'prepare_%s' % resource)(*args, **kwargs)
            except:
                traceback.print_exc()
            if success:
                request.resources.remove((resource, args, kwargs))


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
    @abstractmethod
    def prepare_symbols(self, *args, **kwargs):
        """
        Returns the path to an unzipped symbols directory
        for the given args
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
