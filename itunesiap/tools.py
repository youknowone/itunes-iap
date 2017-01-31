
import warnings
import functools


class lazy_property(object):
    """http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
    """

    def __init__(self, function):
        self.function = function

    def __get__(self, obj, cls):
        value = self.function(obj)
        setattr(obj, self.function.__name__, value)
        return value


def deprecated(func):
    """https://wiki.python.org/moin/PythonDecoratorLibrary#Generating_Deprecation_Warnings

    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {0}.".format(func.__name__),
            category=UserWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)
    return new_func
