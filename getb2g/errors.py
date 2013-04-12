__all__ = ('InvalidResourceException', 'IncompleteRequestException')

class InvalidResourceException(Exception):
    """The requested resource was not valid"""

class IncompleteRequestException(Exception):
    """The requested resource was not valid"""

