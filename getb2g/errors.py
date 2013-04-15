__all__ = ('InvalidResourceException', 'IncompleteRequestException')

class InvalidResourceException(Exception):
    """The requested resource was not valid"""

class IncompleteRequestException(Exception):
    """The requested resource was not valid"""

class MissingDataException(Exception):
    """Not enough information to complete the request"""
    def __init__(self, message=None, *args):
        super(MissingDataException, self).__init__(message or self.__doc__, *args)
