
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""
import json
from mock import patch
import requests
from six import u
import unittest

import itunesiap
from itunesiap import Request, Receipt, set_verification_mode
from itunesiap import exceptions


class TestsIAP(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestsIAP, self).__init__(*args, **kwargs)
        self.iap_response = {
            "receipt": {
                "original_purchase_date_pst": "2010-04-30 08:05:55 America/Los_Angeles",
                "original_transaction_id": "100000004817",
                "original_purchase_date_ms": "133355868",
                "transaction_id": "1000000046178817",
                "quantity": "1",
                "product_id": "com.Product",
                "bvrs": "20120427",
                "purchase_date_ms": "133355868",
                "purchase_date": "2010-04-30 15:05:55 Etc/GMT",
                "original_purchase_date": "2010-04-30 15:05:55 Etc/GMT",
                "purchase_date_pst": "2010-04-30 08:05:55 America/Los_Angeles",
                "bid": "com.Example",
                "item_id": "521129812"
            },
            "status": 0
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
        try:
            from testdata import sandbox_receipt
        except ImportError:
            print('No receipt data to test')
            return

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
            mock_post.return_value.content = json.dumps(iap_status_21007)
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
            mock_post.return_value.content = 'Not avaliable'
            mock_post.return_value.status_code = 500
            set_verification_mode('production')
            request = Request('DummyReceipt')
            try:
                receipt = request.validate()
            except exceptions.ItunesServerNotAvailable as e:
                assert e[0] == 500
                assert e[1] == 'Not avaliable'

    def test_context(self):
        try:
            from testdata import sandbox_receipt
        except ImportError:
            print('No receipt data to test')
            return
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
        receipt = Receipt({u'status': 0, u'receipt': {u'purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles', u'product_id': u'TestProduction1', u'original_transaction_id': u'1000000012345678', u'unique_identifier': u'bcbdb3d45543920dd9sd5c79a72948001fc22a39', u'original_purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles', u'original_purchase_date': u'2013-01-01 00:00:00 Etc/GMT', u'bvrs': u'1.0', u'original_purchase_date_ms': u'1348200000000', u'purchase_date': u'2013-01-01 00:00:00 Etc/GMT', u'item_id': u'500000000', u'purchase_date_ms': u'134820000000', u'bid': u'org.youknowone.itunesiap', u'transaction_id': u'1000000012345678', u'quantity': u'1'}})

        assert receipt.status == 0  # 0 is normal
        assert receipt.product_id == u'TestProduction1'  #
        assert receipt.original_transaction_id == u'1000000012345678'  # original transaction id
        assert receipt.quantity == u'1'  # check quantity
        assert receipt.unique_identifier == u'bcbdb3d45543920dd9sd5c79a72948001fc22a39'

    def test_shortcut(self):
        try:
            from testdata import sandbox_receipt
        except ImportError:
            print('No receipt data to test')
            return
        mode = itunesiap.get_verification_mode()
        itunesiap.set_verification_mode('sandbox')
        itunesiap.verify(sandbox_receipt)
        itunesiap.set_verification_mode(mode)


if __name__ == '__main__':
    unittest.main()
