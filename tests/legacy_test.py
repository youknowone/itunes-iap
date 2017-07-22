
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""
import json
from mock import patch
import requests
import unittest

import itunesiap.legacy as itunesiap
from itunesiap.legacy import Request, Receipt, set_verification_mode
from itunesiap.legacy import exceptions

from tests.conftest import raw_receipt_legacy


class TestsIAP(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestsIAP, self).__init__(*args, **kwargs)
        self.iap_response = {
            u'status': 0,
            u'receipt': {
                u'purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles',
                u'product_id': u'TestProduction1',
                u'original_transaction_id': u'1000000012345678',
                u'unique_identifier': u'bcbdb3d45543920dd9sd5c79a72948001fc22a39',
                u'original_purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles',
                u'original_purchase_date': u'2013-01-01 00:00:00 Etc/GMT',
                u'bvrs': u'1.0',
                u'original_purchase_date_ms': u'1348200000000',
                u'purchase_date': u'2013-01-01 00:00:00 Etc/GMT',
                u'item_id': u'500000000',
                u'purchase_date_ms': u'134820000000',
                u'bid': u'org.youknowone.itunesiap',
                u'transaction_id': u'1000000012345678',
                u'quantity': u'1'
            }
        }

        # Response with multiple in_app's
        self.iap_response_in_app = {
            u'status': 0,
            u'receipt': {
                u'original_purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles',
                u'version_external_identifier': 0,
                u'original_purchase_date': u'2013-01-01 07:00:00 Etc/GMT',
                u'in_app': [
                    {
                        u'is_trial_period': u'false',
                        u'purchase_date_pst': u'2013-05-18 20:21:09 America/Los_Angeles',
                        u'product_id': u'org.itunesiap',
                        u'original_transaction_id': u'1000000155715958',
                        u'original_purchase_date_pst': u'2013-05-18 19:29:45 America/Los_Angeles',
                        u'original_purchase_date': u'2013-05-19 02:29:45 Etc/GMT',
                        u'original_purchase_date_ms': u'1432002585000',
                        u'purchase_date': u'2013-05-19 03:21:09 Etc/GMT',
                        u'purchase_date_ms': u'1432005669000',
                        u'transaction_id': u'1000000155715958',
                        u'quantity': u'1'
                    },
                    {
                        u'is_trial_period': u'false',
                        u'purchase_date_pst': u'2013-05-19 20:21:09 America/Los_Angeles',
                        u'product_id': u'org.itunesiap',
                        u'original_transaction_id': u'1000000155718067',
                        u'original_purchase_date_pst': u'2013-05-18 19:37:10 America/Los_Angeles',
                        u'original_purchase_date': u'2013-05-19 02:37:10 Etc/GMT',
                        u'original_purchase_date_ms': u'1432003030000',
                        u'purchase_date': u'2013-05-19 03:21:09 Etc/GMT',
                        u'purchase_date_ms': u'1432005669000',
                        u'transaction_id': u'1000000155718067',
                        u'quantity': u'1'
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
        sandbox_receipt = raw_receipt_legacy()

        set_verification_mode('production')
        request = Request(sandbox_receipt)
        try:
            receipt = request.verify()
            assert False
        except exceptions.InvalidReceipt as e:
            assert e.status == 21007
            assert e.description == e._descriptions[21007]
        set_verification_mode('sandbox')
        request = Request(sandbox_receipt)
        receipt = request.verify()
        assert receipt

    def test_responses(self):
        # We're going to mock the Apple's response and put 21007 status
        with patch.object(requests, 'post') as mock_post:
            iap_status_21007 = self.iap_response.copy()
            iap_status_21007['status'] = 21007
            mock_post.return_value.content = json.dumps(iap_status_21007).encode('utf-8')
            mock_post.return_value.status_code = 200
            set_verification_mode('production')
            request = Request('DummyReceipt')
            try:
                request.verify()
            except exceptions.InvalidReceipt as e:
                assert e.status == 21007
                assert e.description == e._descriptions[21007]

        # We're going to return an invalid http status code
        with patch.object(requests, 'post') as mock_post:
            mock_post.return_value.content = 'Not avaliable'
            mock_post.return_value.status_code = 500
            set_verification_mode('production')
            request = Request('DummyReceipt')
            try:
                request.verify()
            except exceptions.ItunesServerNotAvailable as e:
                assert e.args[0] == 500
                assert e.args[1] == 'Not avaliable'

    def test_context(self):
        sandbox_receipt = raw_receipt_legacy()
        request = Request(sandbox_receipt, verify_ssl=True)
        configs = request.use_production, request.use_sandbox
        with request.verification_mode('production'):
            try:
                request.verify()
                assert False
            except exceptions.InvalidReceipt as e:
                assert e.status == 21007
            with request.verification_mode('review'):
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
        assert receipt.product_id == u'TestProduction1'  #
        assert receipt.original_transaction_id == u'1000000012345678'  # original transaction id
        assert receipt.quantity == u'1'  # check quantity
        assert receipt.unique_identifier == u'bcbdb3d45543920dd9sd5c79a72948001fc22a39'

    def test_shortcut(self):
        sandbox_receipt = raw_receipt_legacy()
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
        assert ext_receipt['receipt']['product_id'] == u'TestProduction1'
        assert ext_receipt['receipt']['original_transaction_id'] == u'1000000012345678'  # original transaction id
        assert ext_receipt['receipt']['quantity'] == u'1'  # check quantity

        # Test IAP Response with in_app list
        request = Request('DummyReceipt', use_production=True)
        ext_receipt = request._extract_receipt(self.iap_response_in_app)

        assert ext_receipt['status'] == 0  # 0 is normal
        assert ext_receipt['receipt']['product_id'] == u'org.itunesiap'
        assert ext_receipt['receipt']['original_transaction_id'] == u'1000000155718067'  # original transaction id
        assert ext_receipt['receipt']['quantity'] == u'1'  # check quantity


if __name__ == '__main__':
    unittest.main()
