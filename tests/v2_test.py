
"""See official document [#documnet]_ for more information.

.. [#document] https://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/StoreKitGuide/VerifyingStoreReceipts/VerifyingStoreReceipts.html#//apple_ref/doc/uid/TP40008267-CH104-SW1
"""

import json
import requests
from mock import patch

import pytest
import itunesiap

LEGACY_RAW_RECEIPT = '''ewoJInNpZ25hdHVyZSIgPSAiQW1vSjJDNFhra1hXcngwbDBwMUVCMkhqdndWRkJPN3NxaHRPYVpYWXNtd29PblU4dkNYNWZJWFV6SmpwWVpwVGJ1bTJhWW5kci9uOHlBc2czUXc0WUZHMUtCbEpLSjU2c1gzcEpmWTRZd2hEMmJsdm1lZVowZ0FXKzNiajBRWGVjUWJORTk5b2duK09janY2U3dFSEdpdkRIY0FRNzBiMTYxekdpbTk2WHVKTkFBQURWekNDQTFNd2dnSTdvQU1DQVFJQ0NHVVVrVTNaV0FTMU1BMEdDU3FHU0liM0RRRUJCUVVBTUg4eEN6QUpCZ05WQkFZVEFsVlRNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURXpNREVHQTFVRUF3d3FRWEJ3YkdVZ2FWUjFibVZ6SUZOMGIzSmxJRU5sY25ScFptbGpZWFJwYjI0Z1FYVjBhRzl5YVhSNU1CNFhEVEE1TURZeE5USXlNRFUxTmxvWERURTBNRFl4TkRJeU1EVTFObG93WkRFak1DRUdBMVVFQXd3YVVIVnlZMmhoYzJWU1pXTmxhWEIwUTJWeWRHbG1hV05oZEdVeEd6QVpCZ05WQkFzTUVrRndjR3hsSUdsVWRXNWxjeUJUZEc5eVpURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd2daOHdEUVlKS29aSWh2Y05BUUVCQlFBRGdZMEFNSUdKQW9HQkFNclJqRjJjdDRJclNkaVRDaGFJMGc4cHd2L2NtSHM4cC9Sd1YvcnQvOTFYS1ZoTmw0WElCaW1LalFRTmZnSHNEczZ5anUrK0RyS0pFN3VLc3BoTWRkS1lmRkU1ckdYc0FkQkVqQndSSXhleFRldngzSExFRkdBdDFtb0t4NTA5ZGh4dGlJZERnSnYyWWFWczQ5QjB1SnZOZHk2U01xTk5MSHNETHpEUzlvWkhBZ01CQUFHamNqQndNQXdHQTFVZEV3RUIvd1FDTUFBd0h3WURWUjBqQkJnd0ZvQVVOaDNvNHAyQzBnRVl0VEpyRHRkREM1RllRem93RGdZRFZSMFBBUUgvQkFRREFnZUFNQjBHQTFVZERnUVdCQlNwZzRQeUdVakZQaEpYQ0JUTXphTittVjhrOVRBUUJnb3Foa2lHOTJOa0JnVUJCQUlGQURBTkJna3Foa2lHOXcwQkFRVUZBQU9DQVFFQUVhU2JQanRtTjRDL0lCM1FFcEszMlJ4YWNDRFhkVlhBZVZSZVM1RmFaeGMrdDg4cFFQOTNCaUF4dmRXLzNlVFNNR1k1RmJlQVlMM2V0cVA1Z204d3JGb2pYMGlreVZSU3RRKy9BUTBLRWp0cUIwN2tMczlRVWU4Y3pSOFVHZmRNMUV1bVYvVWd2RGQ0TndOWXhMUU1nNFdUUWZna1FRVnk4R1had1ZIZ2JFL1VDNlk3MDUzcEdYQms1MU5QTTN3b3hoZDNnU1JMdlhqK2xvSHNTdGNURXFlOXBCRHBtRzUrc2s0dHcrR0szR01lRU41LytlMVFUOW5wL0tsMW5qK2FCdzdDMHhzeTBiRm5hQWQxY1NTNnhkb3J5L0NVdk02Z3RLc21uT09kcVRlc2JwMGJzOHNuNldxczBDOWRnY3hSSHVPTVoydG04bnBMVW03YXJnT1N6UT09IjsKCSJwdXJjaGFzZS1pbmZvIiA9ICJld29KSW05eWFXZHBibUZzTFhCMWNtTm9ZWE5sTFdSaGRHVXRjSE4wSWlBOUlDSXlNREV5TFRBNUxUSXdJREU0T2pNeE9qTTRJRUZ0WlhKcFkyRXZURzl6WDBGdVoyVnNaWE1pT3dvSkluVnVhWEYxWlMxcFpHVnVkR2xtYVdWeUlpQTlJQ0kwTW1NeFlqTmtORFUxTmpNNE1qQmtaRGxoTlRsak56bGhOelUyTkRFd01ERm1ZemcxWlRNNUlqc0tDU0p2Y21sbmFXNWhiQzEwY21GdWMyRmpkR2x2YmkxcFpDSWdQU0FpTVRBd01EQXdNREExTmpFMk1UYzJOQ0k3Q2draVluWnljeUlnUFNBaU1TNHdJanNLQ1NKMGNtRnVjMkZqZEdsdmJpMXBaQ0lnUFNBaU1UQXdNREF3TURBMU5qRTJNVGMyTkNJN0Nna2ljWFZoYm5ScGRIa2lJRDBnSWpFaU93b0pJbTl5YVdkcGJtRnNMWEIxY21Ob1lYTmxMV1JoZEdVdGJYTWlJRDBnSWpFek5EZ3hPVEV3T1RneE9USWlPd29KSW5CeWIyUjFZM1F0YVdRaUlEMGdJa0poZEhSc1pVZHZiR1ExTUNJN0Nna2lhWFJsYlMxcFpDSWdQU0FpTlRVME5EazVNekExSWpzS0NTSmlhV1FpSUQwZ0ltTnZiUzUyWVc1cGJHeGhZbkpsWlhwbExtbG5kVzVpWVhSMGJHVWlPd29KSW5CMWNtTm9ZWE5sTFdSaGRHVXRiWE1pSUQwZ0lqRXpORGd4T1RFd09UZ3hPVElpT3dvSkluQjFjbU5vWVhObExXUmhkR1VpSUQwZ0lqSXdNVEl0TURrdE1qRWdNREU2TXpFNk16Z2dSWFJqTDBkTlZDSTdDZ2tpY0hWeVkyaGhjMlV0WkdGMFpTMXdjM1FpSUQwZ0lqSXdNVEl0TURrdE1qQWdNVGc2TXpFNk16Z2dRVzFsY21sallTOU1iM05mUVc1blpXeGxjeUk3Q2draWIzSnBaMmx1WVd3dGNIVnlZMmhoYzJVdFpHRjBaU0lnUFNBaU1qQXhNaTB3T1MweU1TQXdNVG96TVRvek9DQkZkR012UjAxVUlqc0tmUT09IjsKCSJlbnZpcm9ubWVudCIgPSAiU2FuZGJveCI7CgkicG9kIiA9ICIxMDAiOwoJInNpZ25pbmctc3RhdHVzIiA9ICIwIjsKfQ=='''
with itunesiap.env.sandbox:
    LEGACY_RESPONSE = itunesiap.verify(LEGACY_RAW_RECEIPT)._
LEGACY_RESPONSE2 = {
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
RESPONSE = {
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


@pytest.mark.parametrize("raw_receipt", [LEGACY_RAW_RECEIPT])
def test_sandbox_request(raw_receipt):
    """Test sandbox receipt"""
    request = itunesiap.Request(raw_receipt)
    try:
        response = request.verify()
        assert False
    except itunesiap.exc.InvalidReceipt as e:
        assert e.status == 21007
        assert e.description == e._descriptions[21007]

    request = itunesiap.Request(raw_receipt)
    with itunesiap.env.sandbox:
        response = request.verify()
    assert response.status == 0


def test_invalid_responses():
    """Test invalid responses error statuses"""
    # We're going to mock the Apple's response and put 21007 status
    with patch.object(requests, 'post') as mock_post:
        iap_status_21007 = RESPONSE.copy()
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
            assert e.args[0] == 500
            assert e.args[1] == 'Not avaliable'


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
            assert type(e.args[1]) == requests.exceptions.ReadTimeout


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
            assert type(e.args[1]) == requests.exceptions.SSLError


@pytest.mark.parametrize("sandbox_receipt", [LEGACY_RAW_RECEIPT])
def test_context(sandbox_receipt):
    """Test sandbox receipts with real itunes server."""
    request = itunesiap.Request(sandbox_receipt)

    prev_env = itunesiap.env.current()
    assert prev_env != itunesiap.env.production
    with itunesiap.env.production:
        try:
            request.verify()
            assert False
        except itunesiap.exc.InvalidReceipt as e:
            assert e.status == 21007
        with itunesiap.env.review:
            request.verify()
        try:
            request.verify()
            assert False
        except itunesiap.exc.InvalidReceipt as e:
            assert e.status == 21007

    assert prev_env == itunesiap.env.current()

    with itunesiap.env.review.clone(use_sandbox=False) as env:
        assert itunesiap.env.current() == env
        assert env.use_production is True
        assert env.use_sandbox is False

    assert prev_env == itunesiap.env.current()


def test_legacy_receipt():
    """Test legacy receipt responses"""
    response = itunesiap.Response(LEGACY_RESPONSE)

    assert response.status == 0  # 0 is normal

    in_app = response.receipt.last_in_app
    assert in_app.product_id == in_app._product_id == u'BattleGold50'  #
    assert in_app.original_transaction_id == in_app._original_transaction_id == u'1000000056161764'  # original transaction id
    assert in_app._quantity == u'1'  # check quantity
    assert in_app.quantity == 1
    assert in_app._purchase_date == u'2012-09-21 01:31:38 Etc/GMT'

    assert in_app._unique_identifier == u'42c1b3d45563820dd9a59c79a75641001fc85e39'

    response = itunesiap.Response(LEGACY_RESPONSE2)

    assert response.status == 0  # 0 is normal

    in_app = response.receipt.last_in_app
    assert in_app._product_id == u'TestProduction1'  #
    assert in_app._original_transaction_id == u'1000000012345678'  # original transaction id
    assert in_app._quantity == u'1'  # check quantity
    assert in_app._unique_identifier == u'bcbdb3d45543920dd9sd5c79a72948001fc22a39'


def test_receipt():
    response = itunesiap.Response(RESPONSE)

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

    # and that the last_in_app alias is set up correctly
    assert response.receipt.last_in_app == in_app[-1]


def test_shortcut():
    """Test shortcuts"""
    with itunesiap.env.sandbox:
        itunesiap.verify(LEGACY_RAW_RECEIPT)

if __name__ == '__main__':
    pytest.main()
