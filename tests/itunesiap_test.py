
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""

import json
import requests
import pytz
import datetime

from mock import patch

import pytest
import itunesiap


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


def test_invalid_responses(itunes_response):
    """Test invalid responses error statuses"""
    # We're going to mock the Apple's response and put 21007 status
    with patch.object(requests, 'post') as mock_post:
        iap_status_21007 = itunes_response.copy()
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


def test_legacy_receipt1(itunes_response_legacy):
    """Test legacy receipt responses"""
    response = itunesiap.Response(itunes_response_legacy)

    assert response.status == 0  # 0 is normal

    in_app = response.receipt.last_in_app
    assert in_app.product_id == in_app._product_id == u'BattleGold50'  #
    assert in_app.original_transaction_id == in_app._original_transaction_id == u'1000000056161764'  # original transaction id
    assert in_app._quantity == u'1'  # check quantity
    assert in_app.quantity == 1
    assert in_app._purchase_date == u'2012-09-21 01:31:38 Etc/GMT'

    assert in_app._unique_identifier == u'42c1b3d45563820dd9a59c79a75641001fc85e39'


def test_legacy_receipt2(itunes_response_legacy2):
    response = itunesiap.Response(itunes_response_legacy2)

    assert response.status == 0  # 0 is normal

    in_app = response.receipt.last_in_app
    assert in_app._product_id == u'TestProduction1'  #
    assert in_app._original_transaction_id == u'1000000012345678'  # original transaction id
    assert in_app._quantity == u'1'  # check quantity
    assert in_app._unique_identifier == u'bcbdb3d45543920dd9sd5c79a72948001fc22a39'


def test_receipt(itunes_response):
    response = itunesiap.Response(itunes_response)

    assert response.status == 0  # 0 is normal

    # get the in_app property from the respnse
    in_app = response.receipt.in_app
    assert len(in_app) == 2

    # test that the InApp object was setup correctly
    in_app0 = in_app[0]
    assert in_app0.product_id == u'org.itunesiap'
    assert in_app0.original_transaction_id == u'1000000155715958'
    assert in_app0.quantity == 1
    assert isinstance(in_app0.is_trial_period, bool)
    assert not in_app0.is_trial_period  # is_trial_period is false
    assert isinstance(in_app0.original_purchase_date_ms, int)
    assert in_app0.original_purchase_date_ms == 1432002585000
    assert isinstance(in_app0.purchase_date_ms, int)
    assert in_app0.purchase_date_ms == 1432005669000
    assert in_app0.purchase_date == datetime.datetime(2013, 5, 19, 3, 21, 9).replace(tzinfo=pytz.UTC)
    assert in_app0._purchase_date == '2013-05-19 03:21:09 Etc/GMT'
    assert in_app0._purchase_date == in_app0['purchase_date']

    # and that the last_in_app alias is set up correctly
    assert response.receipt.last_in_app == in_app[-1]

    with pytest.raises(AttributeError):
        response.receipt.in_app[0].expires_date
    with pytest.raises(KeyError):
        response.receipt.in_app[0].expires_date
        # ensure we can also catch this with KeyError due to backward compatibility


def test_shortcut(raw_receipt_legacy):
    """Test shortcuts"""
    itunesiap.verify(raw_receipt_legacy, env=itunesiap.env.sandbox)


def test_date():
    """Test to parse string dates to python dates"""
    import pytz
    import datetime

    d = itunesiap.receipt._to_datetime(u'2013-01-01T00:00:00+09:00')
    assert (d.year, d.month, d.day) == (2013, 1, 1)
    assert d.tzinfo._offset == datetime.timedelta(0, 9 * 3600)

    d = itunesiap.receipt._to_datetime(u'2013-01-01 00:00:00 Etc/GMT')
    assert (d.year, d.month, d.day) == (2013, 1, 1)
    assert d.tzinfo._utcoffset == datetime.timedelta(0)

    d = itunesiap.receipt._to_datetime(u'2013-01-01 00:00:00 America/Los_Angeles')
    assert (d.year, d.month, d.day) == (2013, 1, 1)
    assert d.tzinfo == pytz.timezone('America/Los_Angeles')

    with pytest.raises(ValueError):
        itunesiap.receipt._to_datetime(u'wrong date')


@pytest.mark.parametrize("object", [
    itunesiap.Request('DummyReceipt'),
    itunesiap.Response('{}'),
])
def test_repr(object):
    """Test __repr__"""
    '{0!r}'.format(object)


if __name__ == '__main__':
    pytest.main()
