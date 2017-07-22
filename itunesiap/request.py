""":mod:`itunesiap.request`"""
import json
import functools

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
    For detail, see also the Apple document: `<https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html>`_.

    :param str receipt_data: An iTunes receipt data as Base64 encoded string.
    :param str password: Only used for receipts that contain auto-renewable subscriptions. Your app's shared secret (a hexadecimal string).
    :param bool exclude_old_transactions: Only used for iOS7 style app receipts that contain auto-renewable or non-renewing subscriptions. If value is true, response includes only the latest renewal transaction for any subscriptions.
    :param proxy_url: A proxy url to access the iTunes validation url.
        (It is an attribute of :func:`verify` but misplaced here)
    """

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

    def verify_from(self, url, timeout=None, verify_ssl=True):
        """The actual implemention of verification request.

        :func:`verify` calls this method to try to verifying for each servers.

        :param str url: iTunes verification API URL.
        :param float timeout: The value is connection timeout of the verifying
            request. The default value is 30.0 when no `env` is given.
        :param bool verify_ssl: SSL verification.

        :return: :class:`itunesiap.receipt.Receipt` object if succeed.
        :raises: Otherwise raise a request exception.
        """
        post_body = json.dumps(self.request_content)
        requests_post = requests.post
        if self.proxy_url:
            protocol = self.proxy_url.split('://')[0]
            requests_post = functools.partial(requests_post, proxies={protocol: self.proxy_url})
        if timeout is not None:
            requests_post = functools.partial(requests_post, timeout=timeout)
        try:
            http_response = requests_post(url, post_body, verify=verify_ssl)
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

        See also:
            - Receipt_Validation_Programming_Guide_.

        .. _Receipt_Validation_Programming_Guide: https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html

        :param itunesiap.environment.Environment env: Override the environment.
        :param float timeout: The value is connection timeout of the verifying
            request. The default value is 30.0 when no `env` is given.
        :param bool use_production: The value is weather verifying in
            production server or not. The default value is :class:`bool` True
            when no `env` is given.
        :param bool use_sandbox: The value is weather verifying in
            sandbox server or not. The default value is :class:`bool` False
            when no `env` is given.

        :param bool verify_ssl: The value is weather enabling SSL verification
            or not. WARNING: DO NOT TURN IT OFF WITHOUT A PROPER REASON. IF YOU
            DON'T UNDERSTAND WHAT IT MEANS, NEVER SET IT YOURSELF.

        :return: :class:`itunesiap.receipt.Receipt` object if succeed.
        :raises: Otherwise raise a request exception.
        """
        env = options.get('env')
        if not env:  # backward compitibility
            env = Environment._stack[-1]
        use_production = options.get('use_production', env.use_production)
        use_sandbox = options.get('use_sandbox', env.use_sandbox)
        verify_ssl = options.get('verify_ssl', env.verify_ssl)
        timeout = options.get('timeout', env.timeout)
        assert(env.use_production or env.use_sandbox)

        response = None
        if use_production:
            try:
                response = self.verify_from(RECEIPT_PRODUCTION_VALIDATION_URL, timeout=timeout, verify_ssl=verify_ssl)
            except exceptions.InvalidReceipt as e:
                if not use_sandbox or e.status != STATUS_SANDBOX_RECEIPT_ERROR:
                    raise

        if not response and use_sandbox:
            try:
                response = self.verify_from(RECEIPT_SANDBOX_VALIDATION_URL, timeout=timeout, verify_ssl=verify_ssl)
            except exceptions.InvalidReceipt:
                raise

        return response
