"""
itunes-iap
~~~~~~~~~~

Itunes In-app Purchase verification api.

:copyright: (c) 2013 Jeong YunWon
:license: 2-clause BSD.
"""

from .request import Request
from .receipt import Response, Receipt, InApp
from .shortcut import verify, aioverify

from . import exceptions
from . import environment

exc = exceptions
env = environment  # env.default, env.sandbox, env.review


__version__ = '2.6.1'
__all__ = (
    '__version__', 'Request', 'Response', 'Receipt', 'InApp',
    'verify', 'aioverify',
    'exceptions', 'exc', 'environment', 'env')
