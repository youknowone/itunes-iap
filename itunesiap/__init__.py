
"""
    itunes-iap
    ~~~~~~~~~~

    Itunes In-app Purchase verification api.

    :copyright: (c) 2013 Jeong YunWon
    :license: 2-clause BSD.
"""

import pkg_resources

__version__ = pkg_resources.resource_string('itunesiap', 'version.txt').strip()
VERSION = tuple(int(v) for v in __version__.split('.'))

from .core import Request, Receipt, set_verification_mode
