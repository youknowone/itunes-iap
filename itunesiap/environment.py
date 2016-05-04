
__all__ = ('Environment', 'default', 'production', 'sandbox', 'review', 'current')


class EnvironmentStack(list):
    def push(self, env):
        self.append(env)


class Environment(object):
    """Environement provides option preset for `Request`. `default` is default"""

    ITEMS = ('use_production', 'use_sandbox')
    _stack = EnvironmentStack()

    def __init__(self, **kwargs):
        self.use_production = kwargs.get('use_production', True)
        self.use_sandbox = kwargs.get('use_sandbox', False)
        self.verify_ssl = kwargs.get('verify_ssl', True)

    def clone(self, **kwargs):
        options = self.extract()
        options.update(**kwargs)
        return self.__class__(**options)

    def push(self):
        self._stack.push(self)

    @classmethod
    def pop(self, ctx_id=None):
        if ctx_id is None:
            self._stack.pop(ctx_id)
        else:
            self._stack.pop()

    def __enter__(self):
        self._ctx_id = len(self._stack)
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._stack.pop(self._ctx_id)

    @classmethod
    def current(cls):
        return cls._stack[-1]

    def override(self, **kwargs):
        """Override options in kwargs to given object `self`."""
        for item in self.ITEMS:
            if item in kwargs:
                setattr(self, item, kwargs[item])

    def extract(self):
        """Extract options from `self` and merge to `kwargs` and return new object."""
        options = {}
        for item in self.ITEMS:
            options[item] = getattr(self, item)
        return options

default = Environment(use_production=True, use_sandbox=False, verify_ssl=True)
production = Environment(use_production=True, use_sandbox=False, verify_ssl=True)
sandbox = Environment(use_production=False, use_sandbox=True, verify_ssl=True)
review = Environment(use_production=True, use_sandbox=True, verify_ssl=True)

unsafe = Environment(use_production=True, use_sandbox=True, verify_ssl=False)


default.push()


def current():
    return Environment.current()
