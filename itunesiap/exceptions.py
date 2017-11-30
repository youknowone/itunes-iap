""":mod:`itunesiap.exceptions`"""
from prettyexc import PrettyException as E
from .receipt import Response


class RequestError(E):
    pass


class ItunesServerNotAvailable(RequestError):
    '''iTunes server is not available. No response.'''


class ItunesServerNotReachable(ItunesServerNotAvailable):
    '''iTunes server is not reachable - including connection timeout.'''


class InvalidReceipt(RequestError, Response):
    '''A receipt was given by iTunes server but it has error.'''
    _descriptions = {
        21000: 'The App Store could not read the JSON object you provided.',
        21002: 'The data in the receipt-data property was malformed.',
        21003: 'The receipt could not be authenticated.',
        21004: 'The shared secret you provided does not match the shared secret on file for your account.',
        21005: 'The receipt server is not currently available.',
        21006: 'This receipt is valid but the subscription has expired. When this status code is returned to your server, the receipt data is also decoded and returned as part of the response.',
        21007: 'This receipt is a sandbox receipt, but it was sent to the production service for verification.',
        21008: 'This receipt is a production receipt, but it was sent to the sandbox service for verification.',
    }

    def __init__(self, response_data):
        Response.__init__(self, response_data)
        RequestError.__init__(self, response_data)

    @property
    def description(self):
        return self._descriptions.get(self.status, None)
