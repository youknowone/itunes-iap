
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""
from __future__ import absolute_import

import json
from mock import patch, Mock
import requests
from six import u
import unittest

import itunesiap
from itunesiap import Request, Receipt, set_verification_mode
from itunesiap import exceptions

from .testdata import sandbox_receipt


class TestsIAP(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestsIAP, self).__init__(*args, **kwargs)
        self.iap_response = {
            'status': 0,
            'receipt': {
                'purchase_date_pst': '2013-01-01 00:00:00 America/Los_Angeles',
                'product_id': 'TestProduction1',
                'original_transaction_id': '1000000012345678',
                'unique_identifier': 'bcbdb3d45543920dd9sd5c79a72948001fc22a39',
                'original_purchase_date_pst': '2013-01-01 00:00:00 America/Los_Angeles',
                'original_purchase_date': '2013-01-01 00:00:00 Etc/GMT',
                'bvrs': '1.0',
                'original_purchase_date_ms': '1348200000000',
                'purchase_date': '2013-01-01 00:00:00 Etc/GMT',
                'item_id': '500000000',
                'purchase_date_ms': '134820000000',
                'bid': 'org.youknowone.itunesiap',
                'transaction_id': '1000000012345678',
                'quantity': '1'
            }
        }

        # Response with multiple in_app's
        self.iap_response_in_app = {
            'status': 0,
            'receipt': {
                'original_purchase_date_pst': '2013-01-01 00:00:00 America/Los_Angeles',
                'version_external_identifier': 0,
                'original_purchase_date': '2013-01-01 07:00:00 Etc/GMT',
                'in_app': [
                    {
                        'is_trial_period': 'false',
                        'purchase_date_pst': '2013-05-18 20:21:09 America/Los_Angeles',
                        'product_id': 'org.itunesiap',
                        'original_transaction_id': '1000000155715958',
                        'original_purchase_date_pst': '2013-05-18 19:29:45 America/Los_Angeles',
                        'original_purchase_date': '2013-05-19 02:29:45 Etc/GMT',
                        'original_purchase_date_ms': '1432002585000',
                        'purchase_date': '2013-05-19 03:21:09 Etc/GMT',
                        'purchase_date_ms': '1432005669000',
                        'transaction_id': '1000000155715958',
                        'quantity': '1'
                    },
                    {
                        'is_trial_period': 'false',
                        'purchase_date_pst': '2013-05-19 20:21:09 America/Los_Angeles',
                        'product_id': 'org.itunesiap',
                        'original_transaction_id': '1000000155718067',
                        'original_purchase_date_pst': '2013-05-18 19:37:10 America/Los_Angeles',
                        'original_purchase_date': '2013-05-19 02:37:10 Etc/GMT',
                        'original_purchase_date_ms': '1432003030000',
                        'purchase_date': '2013-05-19 03:21:09 Etc/GMT',
                        'purchase_date_ms': '1432005669000',
                        'transaction_id': '1000000155718067',
                        'quantity': '1'
                    }
                ]
            }
        }

    def test_global_mode(self):
        set_verification_mode('production')
        assert Request('').use_production is True
        assert Request('').use_sandbox is False
        set_verification_mode('sandbox')
        assert Request('').use_production is False
        assert Request('').use_sandbox is True
        set_verification_mode('reject')
        assert Request('').use_production is False
        assert Request('').use_sandbox is False
        set_verification_mode('review')
        assert Request('').use_production is True
        assert Request('').use_sandbox is True

    def test_request(self):
        set_verification_mode('production')
        request = Request(sandbox_receipt)
        try:
            receipt = request.validate()
            assert False
        except exceptions.InvalidReceipt as e:
            assert e.status == 21007
            assert e.description == e._descriptions[21007]
        set_verification_mode('review')
        request = Request(sandbox_receipt)
        receipt = request.validate()
        assert receipt

    def test_responses(self):
        # We're going to mock the Apple's response and put 21007 status
        with patch.object(requests, 'post') as mock_post:
            iap_status_21007 = self.iap_response.copy()
            iap_status_21007['status'] = 21007
            mock_post.return_value.json = Mock(return_value=iap_status_21007)
            mock_post.return_value.status_code = 200
            set_verification_mode('production')
            request = Request('DummyReceipt')
            try:
                receipt = request.validate()
            except exceptions.InvalidReceipt as e:
                assert e.status == 21007
                assert e.description == e._descriptions[21007]

        # We're going to return an invalid http status code
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.content = 'Not available'
            mock_post.return_value.status_code = 500
            set_verification_mode('production')
            request = Request('DummyReceipt')
            try:
                receipt = request.validate()
            except exceptions.ItunesServerNotAvailable as e:
                assert e[0] == 500
                assert e[1] == 'Not available'

    def test_context(self):
        request = Request(sandbox_receipt)
        configs = request.use_production, request.use_sandbox
        with request.verification_mode('production'):
            try:
                request.verify()
                assert False
            except exceptions.InvalidReceipt as e:
                assert e.status == 21007
            with request.verification_mode('sandbox'):
                request.verify()
            try:
                request.verify()
                assert False
            except exceptions.InvalidReceipt as e:
                assert e.status == 21007
        assert configs == (request.use_production, request.use_sandbox)

    def test_receipt(self):
        receipt = Receipt(self.iap_response)

        assert receipt.status == 0  # 0 is normal
        assert receipt.product_id == 'TestProduction1'  #
        assert receipt.original_transaction_id == '1000000012345678'  # original transaction id
        assert receipt.quantity == '1'  # check quantity
        assert receipt.unique_identifier == 'bcbdb3d45543920dd9sd5c79a72948001fc22a39'

    def test_shortcut(self):
        mode = itunesiap.get_verification_mode()
        itunesiap.set_verification_mode('sandbox')
        itunesiap.verify(sandbox_receipt)
        itunesiap.set_verification_mode(mode)

    def test_extract_receipt(self):
        """
            Testing the extract receipt function.
            The function which helps to put the last 'in_app's fields' in the
            'receipt dictionary'
        """

        # Test IAP Response without in_app list
        request = Request('DummyReceipt', use_production=True)
        ext_receipt = request._extract_receipt(self.iap_response)

        assert ext_receipt['status'] == 0  # 0 is normal
        assert ext_receipt['receipt']['product_id'] == 'TestProduction1'
        assert ext_receipt['receipt']['original_transaction_id'] == '1000000012345678'  # original transaction id
        assert ext_receipt['receipt']['quantity'] == '1'  # check quantity

        # Test IAP Response with in_app list
        request = Request('DummyReceipt', use_production=True)
        ext_receipt = request._extract_receipt(self.iap_response_in_app)

        assert ext_receipt['status'] == 0  # 0 is normal
        assert ext_receipt['receipt']['product_id'] == 'org.itunesiap'
        assert ext_receipt['receipt']['original_transaction_id'] == '1000000155718067'  # original transaction id
        assert ext_receipt['receipt']['quantity'] == '1'  # check quantity

if __name__ == '__main__':
    unittest.main()
