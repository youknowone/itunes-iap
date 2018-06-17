
import itunesiap
import datetime
import pytz
import six

import pytest


rfc3339_to_datetime = itunesiap.receipt._rfc3339_to_datetime
ms_to_datetime = itunesiap.receipt._ms_to_datetime


def test_to_datetime():
    d1 = rfc3339_to_datetime(u'1970-01-01 00:00:00 Etc/GMT')
    d2 = ms_to_datetime(0)
    assert d1 == d2

    d1 = rfc3339_to_datetime(u'2017-09-27 15:04:30 Etc/GMT')
    d2 = ms_to_datetime(1506524670000)
    assert d1 == d2


def test_rfc3339_to_datetime():
    """Test to parse string dates to python dates"""
    d = rfc3339_to_datetime(u'2013-01-01T00:00:00+09:00')
    assert (d.year, d.month, d.day) == (2013, 1, 1)
    assert d.tzinfo._offset == datetime.timedelta(0, 9 * 3600)

    d = rfc3339_to_datetime(u'2013-01-01 00:00:00 Etc/GMT')
    assert (d.year, d.month, d.day) == (2013, 1, 1)
    assert d.tzinfo._utcoffset == datetime.timedelta(0)

    d = rfc3339_to_datetime(u'2013-01-01 00:00:00 America/Los_Angeles')
    assert (d.year, d.month, d.day) == (2013, 1, 1)
    assert d.tzinfo == pytz.timezone('America/Los_Angeles')

    with pytest.raises(ValueError):
        assert rfc3339_to_datetime(u'wrong date')


def test_autorenew_general(itunes_autorenew_response):
    response = itunesiap.Response(itunes_autorenew_response)
    assert response.status == 0
    assert response.receipt  # definitely, no common sense through versions


def test_autorenew_latest(itunes_autorenew_response3):
    response = itunesiap.Response(itunes_autorenew_response3)
    assert response.status == 0
    receipt = response.receipt
    assert receipt.quantity == 1
    assert isinstance(receipt.purchase_date, datetime.datetime)
    assert isinstance(receipt.original_purchase_date, datetime.datetime)
    assert receipt.expires_date.date() == datetime.date(2017, 9, 27)


def test_autorenew_middleage(itunes_autorenew_response2):
    response = itunesiap.Response(itunes_autorenew_response2)
    assert isinstance(response.latest_receipt, six.string_types)

    receipt = response.receipt
    assert isinstance(receipt, itunesiap.receipt.Receipt)
    assert receipt.app_item_id == 0  # 0 only for sandobx
    assert receipt.bundle_id == 'com.example.app'
    assert receipt.application_version == '8'
    assert receipt.version_external_identifier == 0  # 0 only for sandobx
    assert receipt.receipt_creation_date.date() == datetime.date(2017, 7, 25)
    assert receipt.receipt_creation_date_ms == 1500973280000
    itunesiap.receipt.WARN_UNDOCUMENTED_FIELDS = False
    assert receipt.request_date.date() == datetime.date(2017, 7, 27)
    assert receipt.request_date_ms == 1501149119587
    assert receipt.original_purchase_date.date() == datetime.date(2013, 8, 1)
    assert receipt.original_purchase_date_ms == 1375340400000
    itunesiap.receipt.WARN_UNDOCUMENTED_FIELDS = True
    assert receipt.original_application_version == '1.0'

    in_app = receipt.last_in_app
    assert in_app.quantity == 1
    assert in_app.product_id == 'testproduct'
    assert in_app.transaction_id == '1000000318407192'
    assert in_app.original_transaction_id == '1000000318012065'
    assert in_app.purchase_date.date() == datetime.date(2017, 7, 25)
    assert in_app.purchase_date_ms == 1500973279000
    assert in_app.original_purchase_date.date() == datetime.date(2017, 7, 24)
    assert in_app.original_purchase_date_ms == 1500884005000
    assert in_app.expires_date.date() == datetime.date(2017, 7, 25)
    assert in_app.expires_date_ms == 1500973579000
    assert in_app.web_order_line_item_id == '1000000035713887'
    assert in_app.is_trial_period is False

    # latest_receipt_info
    purchase = response.latest_receipt_info[-1]

    assert isinstance(purchase, itunesiap.receipt.Purchase)
    assert purchase.quantity == 1
    assert purchase.product_id == 'testproduct'
    assert purchase.transaction_id == '1000000318420598'
    assert purchase.original_transaction_id == '1000000318012065'
    assert purchase.purchase_date.date() == datetime.date(2017, 7, 25)
    assert purchase.purchase_date_ms == 1500974910000
    assert purchase.original_purchase_date.date() == datetime.date(2017, 7, 24)
    assert purchase.original_purchase_date_ms == 1500884005000
    assert purchase.expires_date.date() == datetime.date(2017, 7, 25)
    assert purchase.expires_date_ms == 1500975210000
    assert purchase.web_order_line_item_id == '1000000035725368'
    assert purchase.is_trial_period is False

    pending_info = response.pending_renewal_info[0]
    assert isinstance(pending_info, itunesiap.receipt.PendingRenewalInfo)
    assert pending_info.expiration_intent == 1
    assert pending_info.auto_renew_product_id == 'testproduct'
    assert pending_info.is_in_billing_retry_period == 0
    assert pending_info.auto_renew_status == 0

    assert receipt.in_app == response.latest_receipt_info[:len(receipt.in_app)]


def test_autorenew_legacy(itunes_autorenew_response_legacy):
    response = itunesiap.Response(itunes_autorenew_response_legacy)
    assert response.receipt.single_purchase == response.latest_receipt_info
    purchase = response.receipt.single_purchase
    with pytest.raises((OverflowError, ValueError)):
        rfc3339_to_datetime(purchase._expires_date)
    assert purchase.expires_date.date() == datetime.date(2012, 12, 2)
    assert purchase.expires_date == rfc3339_to_datetime(purchase._expires_date_formatted)

    assert isinstance(purchase.original_purchase_date, datetime.datetime)
    assert isinstance(purchase.transaction_id, six.string_types)
    assert isinstance(purchase.quantity, six.integer_types)
    assert isinstance(purchase.purchase_date, datetime.datetime)
    assert isinstance(purchase.web_order_line_item_id, six.string_types)
    assert isinstance(purchase.unique_identifier, six.string_types)


def test_autorenew_receipt1(itunes_autorenew_response1):
    response = itunesiap.Response(itunes_autorenew_response1)

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
    assert response.receipt.last_in_app.original_transaction_id == '1000000155718067'

    with pytest.raises(AttributeError):
        assert response.receipt.in_app[0].expires_date
    # ensure we can also catch this with KeyError due to backward compatibility
    with pytest.raises(KeyError):
        assert response.receipt.in_app[0].expires_date


def test_legacy_receipt1(itunes_response_legacy1):
    """Test legacy receipt responses"""
    response = itunesiap.Response(itunes_response_legacy1)

    assert response.status == 0  # 0 is normal

    in_app = response.receipt.last_in_app
    assert in_app.product_id == in_app._product_id == u'BattleGold50'  #
    assert in_app.original_transaction_id == in_app._original_transaction_id == u'1000000056161764'  # original transaction id
    assert in_app._quantity == u'1'  # check quantity
    assert in_app.quantity == 1
    assert in_app._purchase_date == u'2012-09-21 01:31:38 Etc/GMT'

    assert in_app._unique_identifier == u'42c1b3d45563820dd9a59c79a75641001fc85e39'
    assert in_app._unique_identifier == in_app.unique_identifier


def test_legacy_receipt2(itunes_response_legacy2):
    response = itunesiap.Response(itunes_response_legacy2)

    assert response.status == 0  # 0 is normal

    in_app = response.receipt.last_in_app
    assert in_app._product_id == u'TestProduction1'  #
    assert in_app._original_transaction_id == u'1000000012345678'  # original transaction id
    assert in_app._quantity == u'1'  # check quantity
    assert in_app._unique_identifier == u'bcbdb3d45543920dd9sd5c79a72948001fc22a39'
    assert in_app._unique_identifier == in_app.unique_identifier


def test_object_mapper():
    response = itunesiap.Response({'status': 21007, 'unknown': 0})
    assert response.status == 21007  # normal access
    with pytest.raises(AttributeError):
        assert response.unknown
    assert response._unknown == 0  # ok but warning
    with pytest.raises(AttributeError):
        assert response._unknown_field
    with pytest.raises(AttributeError):
        assert response.latest_receipt  # opaque field
    with pytest.raises(AttributeError):
        assert response.receipt  # adapter field
    with pytest.raises(AttributeError):
        assert response.latest_receipt_info  # manually defined field
