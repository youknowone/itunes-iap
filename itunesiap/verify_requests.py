
import json
import functools
import requests

from . import receipt
from . import exceptions
from .environment import Environment


class InvalidReceiptResponse(exceptions.InvalidReceipt, receipt.Response):
    pass


class RequestsVerify(object):
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

        response_data = json.loads(http_response.content.decode('utf-8'))
        response = receipt.Response(response_data)
        if response.status != 0:
            raise exceptions.InvalidReceipt(response_data=response_data)
        return response

    def verify(self, **options):
        """Try verification with current environment.

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
                response = self.verify_from(self.PRODUCTION_VALIDATION_URL, timeout=timeout, verify_ssl=verify_ssl)
            except exceptions.InvalidReceipt as e:
                if not use_sandbox or e.status != self.STATUS_SANDBOX_RECEIPT_ERROR:
                    raise

        if not response and use_sandbox:
            try:
                response = self.verify_from(self.SANDBOX_VALIDATION_URL, timeout=timeout, verify_ssl=verify_ssl)
            except exceptions.InvalidReceipt:
                raise

        return response
