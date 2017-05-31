
import json

import requests

from . import receipt
from . import exceptions
from .environment import Environment

RECEIPT_PRODUCTION_VALIDATION_URL = "https://buy.itunes.apple.com/verifyReceipt"
RECEIPT_SANDBOX_VALIDATION_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
STATUS_SANDBOX_RECEIPT_ERROR = 21007


class Request(object):
    """Validation request with raw receipt.

    Use `verify` method to try verification and get Receipt or exception.

    :param str receipt_data: An iTunes receipt data as Base64 encoded string.
    :param proxy_url: A proxy url to access the iTunes validation url
    """

    def __init__(self, receipt_data, password=None, proxy_url=None, timeout=60):
        self.receipt_data = receipt_data
        self.password = password
        self.proxy_url = proxy_url
        self.timeout = timeout

    def __repr__(self):
        return u'<Request({0}...)>'.format(self.receipt_data[:20])

    @property
    def request_content(self):
        """Build request body for iTunes."""
        if self.password is not None:
            request_content = {'receipt-data': self.receipt_data, 'password': self.password}
        else:
            request_content = {'receipt-data': self.receipt_data}
        return request_content

    def verify_from(self, url, verify_ssl=True):
        """Try verification from given url.

        :param str url: iTunes verification API URL.
        :param bool verify_ssl: SSL verification.

        :return: :class:`itunesiap.receipt.Receipt` object if succeed.
        :raises: Otherwise raise a request exception.
        """
        # If the password exists from kwargs, pass it up with the request, otherwise leave it alone
        post_body = json.dumps(self.request_content)
        try:
            if self.proxy_url:
                protocol = self.proxy_url.split('://')[0]
                http_response = requests.post(url, post_body, verify=verify_ssl, proxies={protocol: self.proxy_url}, timeout=self.timeout)
            else:
                http_response = requests.post(url, post_body, verify=verify_ssl, timeout=self.timeout)
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
        If verify_ssl is true, Apple's SSL certificiate will be
        verified. The verify_ssl is set to false by default for
        backwards compatibility.

        :param Environment env: Override environment if given
        :param bool use_production: Override environment value if given
        :param bool use_sandbox: Override environment value if given
        :param bool verify_ssl: Override environment value if given

        :return: :class:`itunesiap.receipt.Receipt` object if succeed.
        :raises: Otherwise raise a request exception.
        """
        env = options.get('env')
        if not env:
            env = Environment.current()
        use_production = options.get('use_production', env.use_production)
        use_sandbox = options.get('use_sandbox', env.use_sandbox)
        verify_ssl = options.get('verify_ssl', env.verify_ssl)
        assert(env.use_production or env.use_sandbox)

        response = None
        if use_production:
            try:
                response = self.verify_from(RECEIPT_PRODUCTION_VALIDATION_URL, verify_ssl)
                response.env = 'production'
            except exceptions.InvalidReceipt as e:
                if not use_sandbox or e.status != STATUS_SANDBOX_RECEIPT_ERROR:
                    raise

        if not response and use_sandbox:
            try:
                response = self.verify_from(RECEIPT_SANDBOX_VALIDATION_URL, verify_ssl)
                response.env = 'sandbox'
            except exceptions.InvalidReceipt:
                raise

        return response
