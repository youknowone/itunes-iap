""":mod:`itunesiap.environment`

:class:`Environment` is designed to pass pre-defined policies in easy way.
The major use cases are provided as pre-defined constants.

How to use environments
-----------------------

The default policy is `default` and it is the same to `production`. When your
development lifecycle is proceed, you want to change it to `sandbox` or
`review`.

The recommended way to use environments is passing the value to
:func:`itunesiap.verify` function as keyword argument `env`.

.. sourcecode:: python

    >>> itunesiap.verify(receipt, env=itunesiap.env.production)
    >>> itunesiap.verify(receipt, env=itunesiap.env.sandbox)
    >>> itunesiap.verify(receipt, env=itunesiap.env.review)


Review mode
-----------

This is useful when your server is being used both for real users and Apple
reviewers.
Using review mode for a real service is possible, but be aware of: it is not
100% safe. Your testers can getting advantage of free IAP in production
version.
A rough solution what I suggest is:

.. sourcecode:: python

    >>> if client_version == review_version:
    >>>     env = itunesiap.env.review
    >>> else:
    >>>     env = itunesiap.env.production
    >>>
    >>> itunesiap.verify(receipt, env=env)


Environment
-----------
"""
from itunesiap.tools import deprecated

__all__ = ('Environment', 'default', 'production', 'sandbox', 'review')


class EnvironmentStack(list):
    @deprecated
    def push(self, env):
        self.append(env)


class Environment(object):
    """Environment provides option preset for `Request`. `default` is default.

    By passing an environment object to :func:`itunesiap.verify` or
    :func:`itunesiap.request.Request.verify` function, it replaces verifying
    policies.
    """

    ITEMS = (
        'use_production', 'use_sandbox', 'timeout', 'exclude_old_transactions',
        'verify_ssl')

    def __init__(self, **kwargs):
        self.use_production = kwargs.get('use_production', True)
        self.use_sandbox = kwargs.get('use_sandbox', False)
        self.timeout = kwargs.get('timeout', None)
        self.exclude_old_transactions = kwargs.get('exclude_old_transactions', False)
        self.verify_ssl = kwargs.get('verify_ssl', True)

    def __repr__(self):
        return u'<{self.__class__.__name__} use_production={self.use_production} use_sandbox={self.use_sandbox} timeout={self.timeout} exclude_old_transactions={self.exclude_old_transactions} verify_ssl={self.verify_ssl}>'.format(self=self)

    def clone(self, **kwargs):
        """Clone the environment with additional parameter override"""
        options = self.extract()
        options.update(**kwargs)
        return self.__class__(**options)

    def override(self, **kwargs):
        """Override options in kwargs to given object `self`."""
        for item in self.ITEMS:
            if item in kwargs:
                setattr(self, item, kwargs[item])

    def extract(self):
        """Extract options from `self` and merge to `kwargs` then return a new
        dictionary with the values.
        """
        options = {}
        for item in self.ITEMS:
            options[item] = getattr(self, item)
        return options

    # backward compatibility features
    _stack = EnvironmentStack()

    @deprecated
    def push(self):  # pragma: no cover
        self._stack.push(self)

    @deprecated
    def __enter__(self):  # pragma: no cover
        self._ctx_id = len(self._stack)
        self._stack.push(self)
        return self

    @deprecated
    def __exit__(self, exc_type, exc_value, tb):  # pragma: no cover
        self._stack.pop(self._ctx_id)

    @classmethod
    @deprecated
    def current(cls):  # pragma: no cover
        return cls._stack[-1]


#: Use only production server with 30 seconds of timeout.
default = Environment(use_production=True, use_sandbox=False, timeout=30.0, verify_ssl=True)
#: Use only production server with 30 seconds of timeout.
production = Environment(use_production=True, use_sandbox=False, timeout=30.0, verify_ssl=True)
#: Use only sandbox server with 30 seconds of timeout.
sandbox = Environment(use_production=False, use_sandbox=True, timeout=30.0, verify_ssl=True)

review = Environment(use_production=True, use_sandbox=True, timeout=30.0, verify_ssl=True)
#: Use both production and sandbox servers with 30 seconds of timeout.

unsafe = Environment(use_production=True, use_sandbox=True, verify_ssl=False)


Environment._stack.append(default)  # for backward compatibility


@deprecated
def current():
    return Environment.current()
