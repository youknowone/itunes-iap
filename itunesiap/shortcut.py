
from .request import Request


def verify(receipt_data, password=None, proxy_url=None, **kwargs):
    """Shortcut API for :class:`itunesiap.request.Request`

    :param str receipt_data: An iTunes receipt data as Base64 encoded string.
    :param proxy_url: A proxy url to access the itunes validation url
    :param bool use_production: Override environment value if given
    :param bool use_sandbox: Override environment value if given
    :param bool verify_ssl: Override environment value if given

    :return: :class:`itunesiap.receipt.Receipt` object if succeed.
    :raises: Otherwise raise a request exception.
    """
    return Request(receipt_data, password, proxy_url).verify(**kwargs)
