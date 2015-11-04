import os
import unittest

import pytest
import mock
import requests

from itunesiap import Request
from itunesiap import exceptions
from itunesiap.core import RECEIPT_PRODUCTION_VALIDATION_URL, RECEIPT_SANDBOX_VALIDATION_URL
from itunesiap.shortcut import verify

from . import fixtures, vcr


class ItunesIapMixin(object):

    def setUp(self):
        self.password = 'foobar'
        self.receipt_data = open(os.path.join(fixtures, 'valid_receipt.txt')).read().strip()


class ItunesIapTestCase(ItunesIapMixin, unittest.TestCase):

    def setUp(self):
        super(ItunesIapTestCase, self).setUp()
        self.request = Request(self.receipt_data, password=self.password, use_production=False, use_sandbox=True)
        self.dummy_receipt = dict(receipt={}, status=0)

    @vcr.use_cassette('verified_receipt')
    def test_receipt_is_verified(self):
        receipt = self.request.verify()
        assert receipt.status == 0

    """
    @mock.patch.object(Request, 'verify_from')
    def test_try_both_production_and_sandbox_mode(self, verify_mock):
        verify_mock.side_effect = [exceptions.InvalidReceipt, self.dummy_receipt]
        request = Request(self.receipt_data, password=self.password, use_production=True, use_sandbox=True)
        request.verify()
        calls = verify_mock.call_args_list
        assert calls == [mock.call(RECEIPT_PRODUCTION_VALIDATION_URL), mock.call(RECEIPT_SANDBOX_VALIDATION_URL)]
    """

    @mock.patch.object(requests, 'post')
    def test_http_error(self, post_mock):
        post_mock.return_value = mock.MagicMock(status_code=404)
        with pytest.raises(exceptions.ItunesServerNotAvailable):
            self.request.verify()

    @vcr.use_cassette('invalid_receipt_data')
    def test_invalid_receipt(self):
        receipt_data = 'invalid'
        self.request = Request(receipt_data, password=self.password, use_production=False, use_sandbox=True)
        with pytest.raises(exceptions.InvalidReceipt):
            self.request.verify()


class ItunesIapShortcutTestCase(ItunesIapMixin, unittest.TestCase):

    @vcr.use_cassette('verified_receipt')
    def test_verify(self):
        def verify_product(transaction_id):
            if transaction_id != 'foo':
                raise ValueError

        kwargs = dict(password=self.password, use_production=False, use_sandbox=True)

        with pytest.raises(ValueError):
            verify(self.receipt_data, test_paid=verify_product, **kwargs)
