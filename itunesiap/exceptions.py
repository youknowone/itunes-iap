
from prettyexc import PrettyException

class ModeNotAvailable(PrettyException):
    pass

class RequestError(PrettyException):
    pass

class ItunesServerNotAvailable(RequestError):
    pass

class InvalidReceipt(RequestError):
    _req_kwargs_keys = ['status']
