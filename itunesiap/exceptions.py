
class ModeNotAvailable(Exception):
    pass

class RequestError(Exception):
    pass

class ItunesServerNotAvailable(RequestError):
    pass

class InvalidReceipt(RequestError):
    pass
