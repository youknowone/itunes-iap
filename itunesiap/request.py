
import json

import requests

from . import receipt
from . import exceptions
from .environment import Environment

RECEIPT_PRODUCTION_VALIDATION_URL = "https://buy.itunes.apple.com/verifyReceipt"
RECEIPT_SANDBOX_VALIDATION_URL = "https://sandbox.itunes.apple.com/verifyReceipt"


class Request(object):
    """Validation request with raw receipt. Receipt must be base64 encoded string.

    Use `verify` method to try verification and get Receipt or exception.
    """

    def __init__(self, receipt_data, password=None):
        self.receipt_data = receipt_data
        self.password = password

    def __repr__(self):
        return u'<Request({1}...)>'.format(self.receipt_data[:20])

    @property
    def request_content(self):
        if self.password is not None:
            request_content = {'receipt-data': self.receipt_data, 'password': self.password}
        else:
            request_content = {'receipt-data': self.receipt_data}
        return request_content

    def verify_from(self, url, verify_ssl):
        """Try verification from given url."""
        # If the password exists from kwargs, pass it up with the request, otherwise leave it alone
        post_body = json.dumps(self.request_content)
        try:
            http_response = requests.post(url, post_body, verify=verify_ssl)
        except requests.exceptions.RequestException as e:
            raise exceptions.ItunesServerNotReachable(exc=e)

        if http_response.status_code != 200:
            raise exceptions.ItunesServerNotAvailable(http_response.status_code, http_response.content)

        response = receipt.Response(json.loads(http_response.content.decode('utf-8')))
        if response.status != 0:
            raise exceptions.InvalidReceipt(response.status, response=response)
        return response

    def verify(self, **options):
        """Try verification with current environment.
        If verify_request is true, Apple's SSL certificiate will be
        verified. The verify_request is set to false by default for
        backwards compatability.

        Returns a `Receipt` object if succeed. Otherwise raise an exception.
        """
        env = Environment.current()
        use_production = options.get('use_production', env.use_production)
        use_sandbox = options.get('use_sandbox', env.use_sandbox)
        verify_ssl = options.get('verify_ssl', env.verify_ssl)
        assert(env.use_production or env.use_sandbox)

        response = None
        if use_production:
            try:
                response = self.verify_from(RECEIPT_PRODUCTION_VALIDATION_URL, verify_ssl)
            except exceptions.InvalidReceipt:
                if not use_sandbox:
                    raise

        if not response and use_sandbox:
            try:
                response = self.verify_from(RECEIPT_SANDBOX_VALIDATION_URL, verify_ssl)
            except exceptions.InvalidReceipt:
                raise

        return response
