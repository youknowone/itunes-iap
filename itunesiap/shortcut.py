""":mod:`itunesiap.shortcut`"""
from .request import Request


def verify(
        receipt_data, password=None, exclude_old_transactions=False, **kwargs):
    """Shortcut API for :class:`itunesiap.request.Request`.

    See also:
        - Receipt_Validation_Programming_Guide_.

    .. _Receipt_Validation_Programming_Guide: https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html

    :param str receipt_data: :class:`itunesiap.request.Request` argument.
        An iTunes receipt data as Base64 encoded string.
    :param str password: :class:`itunesiap.request.Request` argument. Optional.
        Only used for receipts that contain auto-renewable subscriptions. Your
        app's shared secret (a hexadecimal string).
    :param bool exclude_old_transactions: :class:`itunesiap.request.Request`
        argument. Optional. Only used for iOS7 style app receipts that contain
        auto-renewable or non-renewing subscriptions. If value is true,
        response includes only the latest renewal transaction for any
        subscriptions.

    :param itunesiap.environment.Environment env: Set base environment value.
        See :mod:`itunesiap.environment` for detail.
    :param float timeout: :func:`itunesiap.request.Request.verify` argument.
        Keyword-only optional. The value is connection timeout of the verifying
        request. The default value is 30.0 when no `env` is given.
    :param bool use_production: :func:`itunesiap.request.Request.verify`
        argument. Keyword-only optional. The value is weather verifying in
        production server or not. The default value is :class:`bool` True
        when no `env` is given.
    :param bool use_sandbox: :func:`itunesiap.request.Request.verify`
        argument. Keyword-only optional. The value is weather verifying in
        sandbox server or not. The default value is :class:`bool` False
        when no `env` is given.

    :param bool verify_ssl: :func:`itunesiap.request.Request.verify` argument.
        Keyword-only optional. The value is weather enabling SSL verification
        or not. WARNING: DO NOT TURN IT OFF WITHOUT A PROPER REASON. IF YOU
        DON'T UNDERSTAND WHAT IT MEANS, NEVER SET IT YOURSELF.
    :param str proxy_url: Keyword-only optional. A proxy url to access the
        iTunes validation url.

    :return: :class:`itunesiap.receipt.Receipt` object if succeed.
    :raises: Otherwise raise a request exception in :mod:`itunesiap.exceptions`.
    """
    proxy_url = kwargs.pop('proxy_url', None)
    request = Request(
        receipt_data, password, exclude_old_transactions, proxy_url=proxy_url)
    return request.verify(**kwargs)


def aioverify(
        receipt_data, password=None, exclude_old_transactions=False, **kwargs):
    """Shortcut API for :class:`itunesiap.request.Request`.

    Note that python3.4 support is only available at itunesiap==2.5.1

    For params and returns, see :func:`itunesiap.verify`.
    """
    proxy_url = kwargs.pop('proxy_url', None)
    request = Request(
        receipt_data, password, exclude_old_transactions, proxy_url=proxy_url)
    return request.aioverify(**kwargs)
