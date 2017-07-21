
from .request import Request


def verify(
        receipt_data, password=None, exclude_old_transactions=False, **kwargs):
    """Shortcut API for :class:`itunesiap.request.Request`

    :param str receipt_data: An iTunes receipt data as Base64 encoded string.
    :param proxy_url: A proxy url to access the iTunes validation url
    :param bool use_production: Override environment value if given
    :param bool use_sandbox: Override environment value if given
    :param bool verify_ssl: Override environment value if given

    :return: :class:`itunesiap.receipt.Receipt` object if succeed.
    :raises: Otherwise raise a request exception.
    """
    proxy_url = kwargs.pop('proxy_url', None)
    request = Request(
        receipt_data, password, exclude_old_transactions, proxy_url=proxy_url)
    return request.verify(**kwargs)
