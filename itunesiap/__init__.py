"""
    itunes-iap
    ~~~~~~~~~~

    Itunes In-app Purchase verification api.

    :copyright: (c) 2013 Jeong YunWon
    :license: 2-clause BSD.
"""

from six import PY3
import pkg_resources

__version__ = pkg_resources.resource_string('itunesiap', 'version.txt').strip()
if PY3:
    __version__ = __version__.decode('ascii')
VERSION = tuple(int(v) for v in __version__.split('.'))

from .core import Request, Receipt, set_verification_mode
from .exceptions import InvalidReceipt, ModeNotAvailable, RequestError
from .shortcut import verify

