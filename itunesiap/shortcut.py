
from .request import Request


def verify(*args, **kwargs):
    return Request(*args, **kwargs).verify()
