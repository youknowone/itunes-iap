
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""

import json
import requests
import itunesiap

import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_sandbox_request(raw_receipt_legacy):
    """Test sandbox receipt"""
    raw_receipt = raw_receipt_legacy
    request = itunesiap.Request(raw_receipt)
    try:
        response = request.verify()
        assert False
    except itunesiap.exc.InvalidReceipt as e:
        assert e.status == 21007
        assert e.description == e._descriptions[21007]

    request = itunesiap.Request(raw_receipt)
    response = request.verify(env=itunesiap.env.sandbox)
    assert response.status == 0


def test_old_transaction_exclusion(raw_receipt_legacy):
    """Test optional old transaction exclusion parameter"""
    raw_receipt = raw_receipt_legacy
    request = itunesiap.Request(raw_receipt)
    response = request.verify(exclude_old_transactions=True, env=itunesiap.env.sandbox)
    assert response.status == 0


def test_invalid_responses(itunes_response_legacy2):
    """Test invalid responses error statuses"""
    # We're going to mock the Apple's response and put 21007 status
    with patch.object(requests, 'post') as mock_post:
        iap_status_21007 = itunes_response_legacy2.copy()
        iap_status_21007['status'] = 21007
        mock_post.return_value.content = json.dumps(iap_status_21007).encode('utf-8')
        mock_post.return_value.status_code = 200

        request = itunesiap.Request('DummyReceipt')
        try:
            request.verify()
        except itunesiap.exc.InvalidReceipt as e:
            assert e.status == 21007
            assert e.description == e._descriptions[21007]


def test_itunes_not_available():
    """Test itunes server errors"""
    # We're going to return an invalid http status code
    with patch.object(requests, 'post') as mock_post:
        mock_post.return_value.content = 'Not avaliable'
        mock_post.return_value.status_code = 500
        request = itunesiap.Request('DummyReceipt')
        try:
            request.verify()
        except itunesiap.exc.ItunesServerNotAvailable as e:
            assert e[0] == 500
            assert e[1] == 'Not avaliable'


def test_request_fail():
    """Test failure making request to itunes server """
    # We're going to return an invalid http status code
    with patch.object(requests, 'post') as mock_post:
        mock_post.side_effect = requests.exceptions.ReadTimeout('Timeout')
        request = itunesiap.Request('DummyReceipt')
        try:
            request.verify()
            assert False
        except itunesiap.exc.RequestError as e:
            assert type(e['exc']) == requests.exceptions.ReadTimeout


def test_ssl_request_fail():
    """Test failure making request to itunes server """
    # We're going to return an invalid http status code
    with patch.object(requests, 'post') as mock_post:
        mock_post.side_effect = requests.exceptions.SSLError('Bad ssl')
        request = itunesiap.Request('DummyReceipt')
        try:
            request.verify(verify_request=True)
            assert False
        except itunesiap.exc.RequestError as e:
            assert type(e['exc']) == requests.exceptions.SSLError


def test_invalid_receipt():
    request = itunesiap.Request('wrong receipt')

    with pytest.raises(itunesiap.exc.InvalidReceipt):
        request.verify(env=itunesiap.env.production)

    with pytest.raises(itunesiap.exc.InvalidReceipt):
        request.verify(env=itunesiap.env.sandbox)

    try:
        itunesiap.verify('bad data')
    except itunesiap.exc.InvalidReceipt as e:
        print(e)  # __str__ test
        print(repr(e))  # __repr__ test


def test_timeout():
    with pytest.raises(itunesiap.exceptions.ItunesServerNotReachable):
        itunesiap.verify('DummyReceipt', timeout=0.0001)


def test_shortcut(raw_receipt_legacy):
    """Test shortcuts"""
    itunesiap.verify(raw_receipt_legacy, env=itunesiap.env.sandbox)


@pytest.mark.parametrize("object", [
    itunesiap.Request('DummyReceipt'),
    itunesiap.Response('{}'),
    itunesiap.environment.Environment(),
])
def test_repr(object):
    """Test __repr__"""
    '{0!r}'.format(object)


if __name__ == '__main__':
    pytest.main()
