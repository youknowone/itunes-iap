
"""
https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""
from itunesiap import Request, Receipt, set_validation_mode
from itunesiap import exceptions

def test_mode():
    set_validation_mode('production')
    assert Request('').use_production == True 
    assert Request('').use_sandbox == False 
    set_validation_mode('sandbox')
    assert Request('').use_production == False 
    assert Request('').use_sandbox == True
    set_validation_mode('reject')
    assert Request('').use_production == False 
    assert Request('').use_sandbox == False 
    set_validation_mode('review')
    assert Request('').use_production == True 
    assert Request('').use_sandbox == True

def test_request():
    try:
        from testdata import sandbox_receipt
    except ImportError:
        print 'No receipt data to test'
        return

    set_validation_mode('production')
    request = Request(sandbox_receipt)
    try:
        receipt = request.validate()
        assert False
    except exceptions.InvalidReceipt:
        pass
    set_validation_mode('review')
    request = Request(sandbox_receipt)
    receipt = request.validate()
    assert receipt

def test_receipt():
    receipt = Receipt({u'status': 0, u'receipt': {u'purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles', u'product_id': u'TestProduction1', u'original_transaction_id': u'1000000012345678', u'unique_identifier': u'bcbdb3d45543920dd9sd5c79a72948001fc22a39', u'original_purchase_date_pst': u'2013-01-01 00:00:00 America/Los_Angeles', u'original_purchase_date': u'2013-01-01 00:00:00 Etc/GMT', u'bvrs': u'1.0', u'original_purchase_date_ms': u'1348200000000', u'purchase_date': u'2013-01-01 00:00:00 Etc/GMT', u'item_id': u'500000000', u'purchase_date_ms': u'134820000000', u'bid': u'org.youknowone.itunesiap', u'transaction_id': u'1000000012345678', u'quantity': u'1'}})

    assert receipt.status == 0 # 0 is normal
    assert receipt.product_id == u'TestProduction1' # 
    assert receipt.original_transaction_id == u'1000000012345678' # original transaction id
    assert receipt.quantity == u'1' # check quantity
    assert receipt.unique_identifier == u'bcbdb3d45543920dd9sd5c79a72948001fc22a39'

if __name__ == '__main__':
    symbols = globals().keys()
    for k in symbols:
        if k.startswith('test_'):
            globals()[k]()

