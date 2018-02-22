import asyncio
import json
import aiohttp

from . import receipt
from . import exceptions
from .environment import default as default_env


class AiohttpVerify:

    async def aioverify_from(self, url, timeout):
        body = json.dumps(self.request_content).encode()
        async with aiohttp.ClientSession() as session:
            try:
                http_response = await session.post(url, data=body, timeout=timeout)
            except asyncio.TimeoutError as e:
                raise exceptions.ItunesServerNotReachable(exc=e)
            if http_response.status != 200:
                response_text = await http_response.text()
                raise exceptions.ItunesServerNotAvailable(http_response.status, response_text)
            response_body = await http_response.text()
            response_data = json.loads(response_body)
            response = receipt.Response(response_data)
            if response.status != 0:
                raise exceptions.InvalidReceipt(response_data)
            return response

    async def aioverify(self, **options):
        """Try to verify the given receipt with current environment.

        Note that python3.4 support is only available at itunesiap==2.5.1

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

        :param bool verify_ssl: The value will be ignored.

        :return: :class:`itunesiap.receipt.Receipt` object if succeed.
        :raises: Otherwise raise a request exception.
        """
        env = options.get('env', default_env)
        use_production = options.get('use_production', env.use_production)
        use_sandbox = options.get('use_sandbox', env.use_sandbox)
        verify_ssl = options.get('verify_ssl', env.verify_ssl)  # noqa
        timeout = options.get('timeout', env.timeout)

        response = None
        if use_production:
            try:
                response = await self.aioverify_from(self.PRODUCTION_VALIDATION_URL, timeout=timeout)
            except exceptions.InvalidReceipt as e:
                if not use_sandbox or e.status != self.STATUS_SANDBOX_RECEIPT_ERROR:
                    raise
        if not response and use_sandbox:
            try:
                response = await self.aioverify_from(self.SANDBOX_VALIDATION_URL, timeout=timeout)
            except exceptions.InvalidReceipt as e:
                raise
        return response
