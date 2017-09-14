""":mod:`itunesiap.request`"""

from itunesiap.verify_requests import RequestsVerify

try:
    from itunesiap.verify_aiohttp import AiohttpVerify
except (SyntaxError, ImportError, AttributeError):  # pragma: no cover
    class AiohttpVerify(object):
        pass


class RequestBase(object):

    PRODUCTION_VALIDATION_URL = "https://buy.itunes.apple.com/verifyReceipt"
    SANDBOX_VALIDATION_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
    STATUS_SANDBOX_RECEIPT_ERROR = 21007

    def __init__(
            self, receipt_data, password=None, exclude_old_transactions=False,
            **kwargs):
        self.receipt_data = receipt_data
        self.password = password
        self.exclude_old_transactions = exclude_old_transactions
        self.proxy_url = kwargs.pop('proxy_url', None)
        if kwargs:  # pragma: no cover
            raise TypeError(
                u"__init__ got unexpected keyword argument {}".format(
                    ', '.join(kwargs.keys())))

    def __repr__(self):
        return u'<Request({0}...)>'.format(self.receipt_data[:20])

    @property
    def request_content(self):
        """Instantly built request body for iTunes."""
        request_content = {
            'receipt-data': self.receipt_data,
            'exclude-old-transactions': self.exclude_old_transactions}
        if self.password is not None:
            request_content['password'] = self.password
        return request_content


class Request(RequestBase, RequestsVerify, AiohttpVerify):
    """Validation request with raw receipt.

    Use `verify` method to try verification and get Receipt or exception.
    For detail, see also the Apple document: `<https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html>`_.

    :param str receipt_data: An iTunes receipt data as Base64 encoded string.
    :param str password: Only used for receipts that contain auto-renewable subscriptions. Your app's shared secret (a hexadecimal string).
    :param bool exclude_old_transactions: Only used for iOS7 style app receipts that contain auto-renewable or non-renewing subscriptions. If value is true, response includes only the latest renewal transaction for any subscriptions.
    :param proxy_url: A proxy url to access the iTunes validation url.
        (It is an attribute of :func:`verify` but misplaced here)
    """
