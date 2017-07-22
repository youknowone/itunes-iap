"""
itunes-iap
~~~~~~~~~~

Itunes In-app Purchase verification api.

:copyright: (c) 2013 Jeong YunWon - 2014 Andy Briggs
:license: 2-clause BSD.
"""

from six import PY3

from .request import Request
from .receipt import Response, Receipt, InApp
from .shortcut import verify

from . import exceptions
from . import environment

exc = exceptions
env = environment  # env.default, env.sandbox, env.review

try:
    import pkg_resources
except ImportError:  # pragma: no cover
    __version__ = VERSION = None
else:
    __version__ = pkg_resources.resource_string(
        'itunesiap', 'version.txt').strip()
    if PY3:
        __version__ = __version__.decode('ascii')  # pragma: no cover
    VERSION = tuple(int(v) for v in __version__.split('.'))


__all__ = (
    'Request', 'Response', 'Receipt', 'InApp', 'verify',
    'exceptions', 'exc', 'environment', 'env')
