
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""

import asyncio

import pytest
import itunesiap


@pytest.mark.asyncio
@asyncio.coroutine
def test_sandbox_aiorequest(raw_receipt_legacy):
    """Test sandbox receipt"""
    raw_receipt = raw_receipt_legacy
    request = itunesiap.Request(raw_receipt)
    try:
        response = yield from request.aioverify()
    except itunesiap.exc.InvalidReceipt as e:
        assert e.status == 21007
        assert e.description == e._descriptions[21007]
    else:
        assert False, response
    response = yield from request.aioverify(env=itunesiap.env.sandbox)
    assert response.status == 0


@pytest.mark.asyncio
@asyncio.coroutine
def test_invalid_receipt():
    request = itunesiap.Request('wrong receipt')

    with pytest.raises(itunesiap.exc.InvalidReceipt):
        yield from request.aioverify(env=itunesiap.env.production)

    with pytest.raises(itunesiap.exc.InvalidReceipt):
        yield from request.aioverify(env=itunesiap.env.sandbox)


@pytest.mark.skip
@pytest.mark.asyncio
@asyncio.coroutine
def test_timeout():
    with pytest.raises(itunesiap.exceptions.ItunesServerNotReachable):
        yield from itunesiap.aioverify(
            'DummyReceipt', timeout=0.000001, env=itunesiap.env.review)


def test_shortcut(raw_receipt_legacy):
    """Test shortcuts"""
    itunesiap.aioverify(raw_receipt_legacy, env=itunesiap.env.sandbox)
