__all__ = ('InvalidResourceException', 'IncompleteRequestException', 'MissingDataException', 'MultipleDeviceResourceException')

class GetB2GException(Exception):
    def __init__(self, *args, **kwargs):
        msg = kwargs.get('msg') or self.__doc__
        super(GetB2GException, self).__init__(msg, *args, **kwargs)

class InvalidResourceException(GetB2GException):
    """The requested resource is not valid"""

class IncompleteRequestException(GetB2GException):
    """The requested resource is not valid"""

class MissingDataException(GetB2GException):
    """Not enough information to complete the request"""

class MultipleDeviceResourceException(GetB2GException):
    """Not allowed to have more than one device resource"""
