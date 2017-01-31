
from . import exceptions
from .tools import deprecated
import requests
import json
import contextlib
from prettyexc import PrettyException as E


RECEIPT_PRODUCTION_VALIDATION_URL = "https://buy.itunes.apple.com/verifyReceipt"
RECEIPT_SANDBOX_VALIDATION_URL = "https://sandbox.itunes.apple.com/verifyReceipt"


USE_PRODUCTION = True
USE_SANDBOX = False


class ModeNotAvailable(E):
    message = '`mode` should be one of `production`, `sandbox`, `review`, `reject`'


exceptions.ModeNotAvailable = ModeNotAvailable


def config_from_mode(mode):
    if mode not in ('production', 'sandbox', 'review', 'reject'):
        raise exceptions.ModeNotAvailable(mode)
    production = mode in ('production', 'review')
    sandbox = mode in ('sandbox', 'review')
    return production, sandbox


def set_verification_mode(mode):
    """Set global verification mode that where allows production or sandbox.
    `production`, `sandbox`, `review` or `reject` available. Otherwise raise
    an exception.

    `production`: Allows production receipts only. Default.
    `sandbox`: Allows sandbox receipts only.
    `review`: Allows production receipts but use sandbox as fallback.
    `reject`: Reject all receipts.
    """
    global USE_PRODUCTION, USE_SANDBOX
    USE_PRODUCTION, USE_SANDBOX = config_from_mode(mode)


def get_verification_mode():
    if USE_PRODUCTION and USE_SANDBOX:
        return 'review'
    if USE_PRODUCTION:
        return 'production'
    if USE_SANDBOX:
        return 'sandbox'
    return 'reject'


class Request(object):
    """Validation request with raw receipt. Receipt must be base64 encoded string.

    Use `verify` method to try verification and get Receipt or exception.
    """

    def __init__(self, receipt, password=None, **kwargs):
        self.receipt = receipt
        self.password = password
        self.use_production = kwargs.get('use_production', USE_PRODUCTION)
        self.use_sandbox = kwargs.get('use_sandbox', USE_SANDBOX)
        self.verify_ssl = kwargs.get('verify_ssl', False)
        self.response = None

    def __repr__(self):
        valid = None
        if self.result:
            valid = self.result['status'] == 0
        return u'<Request(valid:{0}, data:{1}...)>'.format(valid, self.receipt[:20])

    @property
    def result(self):
        return self._extract_receipt(json.loads(self.response.content.decode('utf-8')))

    @property
    def request_content(self):
        if self.password is not None:
            request_content = {'receipt-data': self.receipt, 'password': self.password}
        else:
            request_content = {'receipt-data': self.receipt}
        return request_content

    def verify_from(self, url, verify_ssl=False):
        """Try verification from given url."""
        # If the password exists from kwargs, pass it up with the request, otherwise leave it alone
        post_body = json.dumps(self.request_content)
        try:
            self.response = requests.post(url, post_body, verify=verify_ssl)
        except requests.exceptions.RequestException:
            raise

        if self.response.status_code != 200:
            raise exceptions.ItunesServerNotAvailable(self.response.status_code, self.response.content)

        status = self.result['status']
        if status != 0:
            raise exceptions.InvalidReceipt(status, receipt=self.result.get('receipt', None))
        return self.result

    def _extract_receipt(self, receipt_data):
        """There are two formats that iTunes iap purchase receipts are
        sent back in
        """
        if 'receipt' not in receipt_data:
            return receipt_data
        in_app_purchase = receipt_data['receipt'].get('in_app', [])
        if len(in_app_purchase) > 0:
            receipt_data['receipt'].update(in_app_purchase[-1])
        return receipt_data

    @deprecated
    def validate(self):
        return self.verify()

    def verify(self, verify_ssl=None):
        """Try verification with settings. Returns a Receipt object if succeeded.
        Or raise an exception. See `self.response` or `self.result` to see details.
        """
        assert(self.use_production or self.use_sandbox)
        if verify_ssl is None:
            verify_ssl = self.verify_ssl
        if self.use_production:
            try:
                receipt = self.verify_from(RECEIPT_PRODUCTION_VALIDATION_URL, verify_ssl)
            except exceptions.InvalidReceipt:
                if not self.use_sandbox:
                    raise

        if self.use_sandbox:
            try:
                receipt = self.verify_from(RECEIPT_SANDBOX_VALIDATION_URL, verify_ssl)
            except exceptions.InvalidReceipt:
                raise

        return Receipt(receipt)

    @contextlib.contextmanager
    def verification_mode(self, mode):
        configs = self.use_production, self.use_sandbox
        self.use_production, self.use_sandbox = config_from_mode(mode)
        yield
        self.use_production, self.use_sandbox = configs


class Receipt(object):
    """Pretty interface for decoded receipt object.
    """
    def __init__(self, data):
        self.data = data
        self.receipt = data['receipt']
        self.receipt_keys = list(self.receipt.keys())

    def __repr__(self):
        return u'<Receipt({0}, {1})>'.format(self.status, self.receipt)

    @property
    def _(self):
        return self.data

    @property
    def status(self):
        return self.data['status']

    @property
    def latest_receipt(self):
        return self.data['latest_receipt']

    def __getattr__(self, key):
        if key in self.receipt_keys:
            return self.receipt[key]
        try:
            return super(Receipt, self).__getattr__(key)
        except AttributeError:
            return super(Receipt, self).__getattribute__(key)


def verify(data, test_paid=lambda id: id):
    """Convenient verification shortcut.

    :param data: iTunes receipt data
    :param test_paid: Function to test the receipt is paid. Function should
        raise error to disallow response. Parameter is `original_transaction_id`
    :return: :class:`itunesiap.core.Response`
    """
    request = Request(data)
    response = request.verify()
    test_paid(response.original_transaction_id)
    return response
