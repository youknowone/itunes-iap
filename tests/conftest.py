# coding: utf-8
import json
import itunesiap
import pytest
from pytest_lazyfixture import lazy_fixture


def _raw_receipt_legacy():
    return '''ewoJInNpZ25hdHVyZSIgPSAiQW1vSjJDNFhra1hXcngwbDBwMUVCMkhqdndWRkJPN3NxaHRPYVpYWXNtd29PblU4dkNYNWZJWFV6SmpwWVpwVGJ1bTJhWW5kci9uOHlBc2czUXc0WUZHMUtCbEpLSjU2c1gzcEpmWTRZd2hEMmJsdm1lZVowZ0FXKzNiajBRWGVjUWJORTk5b2duK09janY2U3dFSEdpdkRIY0FRNzBiMTYxekdpbTk2WHVKTkFBQURWekNDQTFNd2dnSTdvQU1DQVFJQ0NHVVVrVTNaV0FTMU1BMEdDU3FHU0liM0RRRUJCUVVBTUg4eEN6QUpCZ05WQkFZVEFsVlRNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURXpNREVHQTFVRUF3d3FRWEJ3YkdVZ2FWUjFibVZ6SUZOMGIzSmxJRU5sY25ScFptbGpZWFJwYjI0Z1FYVjBhRzl5YVhSNU1CNFhEVEE1TURZeE5USXlNRFUxTmxvWERURTBNRFl4TkRJeU1EVTFObG93WkRFak1DRUdBMVVFQXd3YVVIVnlZMmhoYzJWU1pXTmxhWEIwUTJWeWRHbG1hV05oZEdVeEd6QVpCZ05WQkFzTUVrRndjR3hsSUdsVWRXNWxjeUJUZEc5eVpURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd2daOHdEUVlKS29aSWh2Y05BUUVCQlFBRGdZMEFNSUdKQW9HQkFNclJqRjJjdDRJclNkaVRDaGFJMGc4cHd2L2NtSHM4cC9Sd1YvcnQvOTFYS1ZoTmw0WElCaW1LalFRTmZnSHNEczZ5anUrK0RyS0pFN3VLc3BoTWRkS1lmRkU1ckdYc0FkQkVqQndSSXhleFRldngzSExFRkdBdDFtb0t4NTA5ZGh4dGlJZERnSnYyWWFWczQ5QjB1SnZOZHk2U01xTk5MSHNETHpEUzlvWkhBZ01CQUFHamNqQndNQXdHQTFVZEV3RUIvd1FDTUFBd0h3WURWUjBqQkJnd0ZvQVVOaDNvNHAyQzBnRVl0VEpyRHRkREM1RllRem93RGdZRFZSMFBBUUgvQkFRREFnZUFNQjBHQTFVZERnUVdCQlNwZzRQeUdVakZQaEpYQ0JUTXphTittVjhrOVRBUUJnb3Foa2lHOTJOa0JnVUJCQUlGQURBTkJna3Foa2lHOXcwQkFRVUZBQU9DQVFFQUVhU2JQanRtTjRDL0lCM1FFcEszMlJ4YWNDRFhkVlhBZVZSZVM1RmFaeGMrdDg4cFFQOTNCaUF4dmRXLzNlVFNNR1k1RmJlQVlMM2V0cVA1Z204d3JGb2pYMGlreVZSU3RRKy9BUTBLRWp0cUIwN2tMczlRVWU4Y3pSOFVHZmRNMUV1bVYvVWd2RGQ0TndOWXhMUU1nNFdUUWZna1FRVnk4R1had1ZIZ2JFL1VDNlk3MDUzcEdYQms1MU5QTTN3b3hoZDNnU1JMdlhqK2xvSHNTdGNURXFlOXBCRHBtRzUrc2s0dHcrR0szR01lRU41LytlMVFUOW5wL0tsMW5qK2FCdzdDMHhzeTBiRm5hQWQxY1NTNnhkb3J5L0NVdk02Z3RLc21uT09kcVRlc2JwMGJzOHNuNldxczBDOWRnY3hSSHVPTVoydG04bnBMVW03YXJnT1N6UT09IjsKCSJwdXJjaGFzZS1pbmZvIiA9ICJld29KSW05eWFXZHBibUZzTFhCMWNtTm9ZWE5sTFdSaGRHVXRjSE4wSWlBOUlDSXlNREV5TFRBNUxUSXdJREU0T2pNeE9qTTRJRUZ0WlhKcFkyRXZURzl6WDBGdVoyVnNaWE1pT3dvSkluVnVhWEYxWlMxcFpHVnVkR2xtYVdWeUlpQTlJQ0kwTW1NeFlqTmtORFUxTmpNNE1qQmtaRGxoTlRsak56bGhOelUyTkRFd01ERm1ZemcxWlRNNUlqc0tDU0p2Y21sbmFXNWhiQzEwY21GdWMyRmpkR2x2YmkxcFpDSWdQU0FpTVRBd01EQXdNREExTmpFMk1UYzJOQ0k3Q2draVluWnljeUlnUFNBaU1TNHdJanNLQ1NKMGNtRnVjMkZqZEdsdmJpMXBaQ0lnUFNBaU1UQXdNREF3TURBMU5qRTJNVGMyTkNJN0Nna2ljWFZoYm5ScGRIa2lJRDBnSWpFaU93b0pJbTl5YVdkcGJtRnNMWEIxY21Ob1lYTmxMV1JoZEdVdGJYTWlJRDBnSWpFek5EZ3hPVEV3T1RneE9USWlPd29KSW5CeWIyUjFZM1F0YVdRaUlEMGdJa0poZEhSc1pVZHZiR1ExTUNJN0Nna2lhWFJsYlMxcFpDSWdQU0FpTlRVME5EazVNekExSWpzS0NTSmlhV1FpSUQwZ0ltTnZiUzUyWVc1cGJHeGhZbkpsWlhwbExtbG5kVzVpWVhSMGJHVWlPd29KSW5CMWNtTm9ZWE5sTFdSaGRHVXRiWE1pSUQwZ0lqRXpORGd4T1RFd09UZ3hPVElpT3dvSkluQjFjbU5vWVhObExXUmhkR1VpSUQwZ0lqSXdNVEl0TURrdE1qRWdNREU2TXpFNk16Z2dSWFJqTDBkTlZDSTdDZ2tpY0hWeVkyaGhjMlV0WkdGMFpTMXdjM1FpSUQwZ0lqSXdNVEl0TURrdE1qQWdNVGc2TXpFNk16Z2dRVzFsY21sallTOU1iM05mUVc1blpXeGxjeUk3Q2draWIzSnBaMmx1WVd3dGNIVnlZMmhoYzJVdFpHRjBaU0lnUFNBaU1qQXhNaTB3T1MweU1TQXdNVG96TVRvek9DQkZkR012UjAxVUlqc0tmUT09IjsKCSJlbnZpcm9ubWVudCIgPSAiU2FuZGJveCI7CgkicG9kIiA9ICIxMDAiOwoJInNpZ25pbmctc3RhdHVzIiA9ICIwIjsKfQ=='''  # noqa


raw_receipt_legacy = pytest.fixture(scope='session')(_raw_receipt_legacy)


@pytest.fixture(scope='session')
def itunes_response_legacy1(raw_receipt_legacy):
    response = itunesiap.verify(raw_receipt_legacy, env=itunesiap.env.sandbox)
    return getattr(response, '_')


@pytest.fixture(scope='session')
def itunes_response_legacy2():
    return {
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


@pytest.fixture(scope='session')
def itunes_autorenew_response_legacy():
    """https://gist.github.com/lxcid/4187607"""
    return json.loads('''{
      "status": 0,
      "latest_receipt_info": {
        "original_purchase_date_ms": "1354432554000",
        "original_purchase_date_pst": "2012-12-01 23:15:54 America/Los_Angeles",
        "transaction_id": "1000000059630000",
        "quantity": "1",
        "bid": "com.example.001",
        "original_transaction_id": "1000000059630000",
        "bvrs": "7",
        "expires_date_formatted": "2012-12-02 08:15:54 Etc/GMT",
        "purchase_date": "2012-12-02 07:15:54 Etc/GMT",
        "expires_date": "1354436154000",
        "product_id": "com.example.premium.1y",
        "purchase_date_ms": "1354432554000",
        "expires_date_formatted_pst": "2012-12-02 00:15:54 America/Los_Angeles",
        "purchase_date_pst": "2012-12-01 23:15:54 America/Los_Angeles",
        "original_purchase_date": "2012-12-02 07:15:54 Etc/GMT",
        "item_id": "580190000",
        "web_order_line_item_id": "1000000026430000",
        "unique_identifier": "0000b0090000"
      },
      "receipt": {
        "original_purchase_date_ms": "1354432554000",
        "original_purchase_date_pst": "2012-12-01 23:15:54 America/Los_Angeles",
        "transaction_id": "1000000059630000",
        "quantity": "1",
        "bid": "com.example.001",
        "original_transaction_id": "1000000059630000",
        "bvrs": "7",
        "expires_date_formatted": "2012-12-02 08:15:54 Etc/GMT",
        "purchase_date": "2012-12-02 07:15:54 Etc/GMT",
        "expires_date": "1354436154000",
        "product_id": "com.example.premium.1y",
        "purchase_date_ms": "1354432554000",
        "expires_date_formatted_pst": "2012-12-02 00:15:54 America/Los_Angeles",
        "purchase_date_pst": "2012-12-01 23:15:54 America/Los_Angeles",
        "original_purchase_date": "2012-12-02 07:15:54 Etc/GMT",
        "item_id": "580190000",
        "web_order_line_item_id": "1000000026430000",
        "unique_identifier": "0000b0090000"
      },
      "latest_receipt": "__ACTUAL_BASE64_ENCODED_RECEIPT"
    }''')


@pytest.fixture(scope='session')
def itunes_autorenew_response1():
    return {
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


@pytest.fixture(scope='session')
def itunes_autorenew_response2():
    """Contributed by Jonas Petersen @jox"""
    return json.loads(r'''{
      "status": 0,
      "environment": "Sandbox",
      "receipt": {
        "receipt_type": "ProductionSandbox",
        "adam_id": 0,
        "app_item_id": 0,
        "bundle_id": "com.example.app",
        "application_version": "8",
        "download_id": 0,
        "version_external_identifier": 0,
        "receipt_creation_date": "2017-07-25 09:01:20 Etc/GMT",
        "receipt_creation_date_ms": "1500973280000",
        "receipt_creation_date_pst": "2017-07-25 02:01:20 America/Los_Angeles",
        "request_date": "2017-07-27 09:51:59 Etc/GMT",
        "request_date_ms": "1501149119587",
        "request_date_pst": "2017-07-27 02:51:59 America/Los_Angeles",
        "original_purchase_date": "2013-08-01 07:00:00 Etc/GMT",
        "original_purchase_date_ms": "1375340400000",
        "original_purchase_date_pst": "2013-08-01 00:00:00 America/Los_Angeles",
        "original_application_version": "1.0",
        "in_app": [
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318012065",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 08:13:24 Etc/GMT",
            "purchase_date_ms": "1500884004000",
            "purchase_date_pst": "2017-07-24 01:13:24 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 08:18:24 Etc/GMT",
            "expires_date_ms": "1500884304000",
            "expires_date_pst": "2017-07-24 01:18:24 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712036",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318014271",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 08:20:19 Etc/GMT",
            "purchase_date_ms": "1500884419000",
            "purchase_date_pst": "2017-07-24 01:20:19 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 08:25:19 Etc/GMT",
            "expires_date_ms": "1500884719000",
            "expires_date_pst": "2017-07-24 01:25:19 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712037",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318015678",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 08:25:19 Etc/GMT",
            "purchase_date_ms": "1500884719000",
            "purchase_date_pst": "2017-07-24 01:25:19 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 08:30:19 Etc/GMT",
            "expires_date_ms": "1500885019000",
            "expires_date_pst": "2017-07-24 01:30:19 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712099",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318021093",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 08:32:23 Etc/GMT",
            "purchase_date_ms": "1500885143000",
            "purchase_date_pst": "2017-07-24 01:32:23 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 08:37:23 Etc/GMT",
            "expires_date_ms": "1500885443000",
            "expires_date_pst": "2017-07-24 01:37:23 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712148",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318022372",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 08:37:23 Etc/GMT",
            "purchase_date_ms": "1500885443000",
            "purchase_date_pst": "2017-07-24 01:37:23 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 08:42:23 Etc/GMT",
            "expires_date_ms": "1500885743000",
            "expires_date_pst": "2017-07-24 01:42:23 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712240",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318024256",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 08:42:23 Etc/GMT",
            "purchase_date_ms": "1500885743000",
            "purchase_date_pst": "2017-07-24 01:42:23 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 08:47:23 Etc/GMT",
            "expires_date_ms": "1500886043000",
            "expires_date_pst": "2017-07-24 01:47:23 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712292",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318060909",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 10:21:48 Etc/GMT",
            "purchase_date_ms": "1500891708000",
            "purchase_date_pst": "2017-07-24 03:21:48 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 10:26:48 Etc/GMT",
            "expires_date_ms": "1500892008000",
            "expires_date_pst": "2017-07-24 03:26:48 America/Los_Angeles",
            "web_order_line_item_id": "1000000035712361",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318063451",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 10:26:51 Etc/GMT",
            "purchase_date_ms": "1500892011000",
            "purchase_date_pst": "2017-07-24 03:26:51 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 10:31:51 Etc/GMT",
            "expires_date_ms": "1500892311000",
            "expires_date_pst": "2017-07-24 03:31:51 America/Los_Angeles",
            "web_order_line_item_id": "1000000035713600",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318065205",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 10:31:51 Etc/GMT",
            "purchase_date_ms": "1500892311000",
            "purchase_date_pst": "2017-07-24 03:31:51 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 10:36:51 Etc/GMT",
            "expires_date_ms": "1500892611000",
            "expires_date_pst": "2017-07-24 03:36:51 America/Los_Angeles",
            "web_order_line_item_id": "1000000035713658",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318066018",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 10:36:51 Etc/GMT",
            "purchase_date_ms": "1500892611000",
            "purchase_date_pst": "2017-07-24 03:36:51 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 10:41:51 Etc/GMT",
            "expires_date_ms": "1500892911000",
            "expires_date_pst": "2017-07-24 03:41:51 America/Los_Angeles",
            "web_order_line_item_id": "1000000035713715",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318067267",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 10:42:17 Etc/GMT",
            "purchase_date_ms": "1500892937000",
            "purchase_date_pst": "2017-07-24 03:42:17 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 10:47:17 Etc/GMT",
            "expires_date_ms": "1500893237000",
            "expires_date_pst": "2017-07-24 03:47:17 America/Los_Angeles",
            "web_order_line_item_id": "1000000035713778",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318069609",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-24 10:47:17 Etc/GMT",
            "purchase_date_ms": "1500893237000",
            "purchase_date_pst": "2017-07-24 03:47:17 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-24 10:52:17 Etc/GMT",
            "expires_date_ms": "1500893537000",
            "expires_date_pst": "2017-07-24 03:52:17 America/Los_Angeles",
            "web_order_line_item_id": "1000000035713845",
            "is_trial_period": "false"
          },
          {
            "quantity": "1",
            "product_id": "testproduct",
            "transaction_id": "1000000318407192",
            "original_transaction_id": "1000000318012065",
            "purchase_date": "2017-07-25 09:01:19 Etc/GMT",
            "purchase_date_ms": "1500973279000",
            "purchase_date_pst": "2017-07-25 02:01:19 America/Los_Angeles",
            "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
            "original_purchase_date_ms": "1500884005000",
            "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
            "expires_date": "2017-07-25 09:06:19 Etc/GMT",
            "expires_date_ms": "1500973579000",
            "expires_date_pst": "2017-07-25 02:06:19 America/Los_Angeles",
            "web_order_line_item_id": "1000000035713887",
            "is_trial_period": "false"
          }
        ]
      },
      "latest_receipt_info": [
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318012065",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 08:13:24 Etc/GMT",
          "purchase_date_ms": "1500884004000",
          "purchase_date_pst": "2017-07-24 01:13:24 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 08:18:24 Etc/GMT",
          "expires_date_ms": "1500884304000",
          "expires_date_pst": "2017-07-24 01:18:24 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712036",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318014271",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 08:20:19 Etc/GMT",
          "purchase_date_ms": "1500884419000",
          "purchase_date_pst": "2017-07-24 01:20:19 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 08:25:19 Etc/GMT",
          "expires_date_ms": "1500884719000",
          "expires_date_pst": "2017-07-24 01:25:19 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712037",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318015678",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 08:25:19 Etc/GMT",
          "purchase_date_ms": "1500884719000",
          "purchase_date_pst": "2017-07-24 01:25:19 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 08:30:19 Etc/GMT",
          "expires_date_ms": "1500885019000",
          "expires_date_pst": "2017-07-24 01:30:19 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712099",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318021093",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 08:32:23 Etc/GMT",
          "purchase_date_ms": "1500885143000",
          "purchase_date_pst": "2017-07-24 01:32:23 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 08:37:23 Etc/GMT",
          "expires_date_ms": "1500885443000",
          "expires_date_pst": "2017-07-24 01:37:23 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712148",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318022372",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 08:37:23 Etc/GMT",
          "purchase_date_ms": "1500885443000",
          "purchase_date_pst": "2017-07-24 01:37:23 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 08:42:23 Etc/GMT",
          "expires_date_ms": "1500885743000",
          "expires_date_pst": "2017-07-24 01:42:23 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712240",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318024256",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 08:42:23 Etc/GMT",
          "purchase_date_ms": "1500885743000",
          "purchase_date_pst": "2017-07-24 01:42:23 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 08:47:23 Etc/GMT",
          "expires_date_ms": "1500886043000",
          "expires_date_pst": "2017-07-24 01:47:23 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712292",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318060909",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 10:21:48 Etc/GMT",
          "purchase_date_ms": "1500891708000",
          "purchase_date_pst": "2017-07-24 03:21:48 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 10:26:48 Etc/GMT",
          "expires_date_ms": "1500892008000",
          "expires_date_pst": "2017-07-24 03:26:48 America/Los_Angeles",
          "web_order_line_item_id": "1000000035712361",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318063451",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 10:26:51 Etc/GMT",
          "purchase_date_ms": "1500892011000",
          "purchase_date_pst": "2017-07-24 03:26:51 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 10:31:51 Etc/GMT",
          "expires_date_ms": "1500892311000",
          "expires_date_pst": "2017-07-24 03:31:51 America/Los_Angeles",
          "web_order_line_item_id": "1000000035713600",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318065205",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 10:31:51 Etc/GMT",
          "purchase_date_ms": "1500892311000",
          "purchase_date_pst": "2017-07-24 03:31:51 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 10:36:51 Etc/GMT",
          "expires_date_ms": "1500892611000",
          "expires_date_pst": "2017-07-24 03:36:51 America/Los_Angeles",
          "web_order_line_item_id": "1000000035713658",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318066018",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 10:36:51 Etc/GMT",
          "purchase_date_ms": "1500892611000",
          "purchase_date_pst": "2017-07-24 03:36:51 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 10:41:51 Etc/GMT",
          "expires_date_ms": "1500892911000",
          "expires_date_pst": "2017-07-24 03:41:51 America/Los_Angeles",
          "web_order_line_item_id": "1000000035713715",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318067267",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 10:42:17 Etc/GMT",
          "purchase_date_ms": "1500892937000",
          "purchase_date_pst": "2017-07-24 03:42:17 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 10:47:17 Etc/GMT",
          "expires_date_ms": "1500893237000",
          "expires_date_pst": "2017-07-24 03:47:17 America/Los_Angeles",
          "web_order_line_item_id": "1000000035713778",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318069609",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-24 10:47:17 Etc/GMT",
          "purchase_date_ms": "1500893237000",
          "purchase_date_pst": "2017-07-24 03:47:17 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-24 10:52:17 Etc/GMT",
          "expires_date_ms": "1500893537000",
          "expires_date_pst": "2017-07-24 03:52:17 America/Los_Angeles",
          "web_order_line_item_id": "1000000035713845",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318407192",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-25 09:01:19 Etc/GMT",
          "purchase_date_ms": "1500973279000",
          "purchase_date_pst": "2017-07-25 02:01:19 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-25 09:06:19 Etc/GMT",
          "expires_date_ms": "1500973579000",
          "expires_date_pst": "2017-07-25 02:06:19 America/Los_Angeles",
          "web_order_line_item_id": "1000000035713887",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318408761",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-25 09:06:19 Etc/GMT",
          "purchase_date_ms": "1500973579000",
          "purchase_date_pst": "2017-07-25 02:06:19 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-25 09:11:19 Etc/GMT",
          "expires_date_ms": "1500973879000",
          "expires_date_pst": "2017-07-25 02:11:19 America/Los_Angeles",
          "web_order_line_item_id": "1000000035725079",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318410476",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-25 09:11:19 Etc/GMT",
          "purchase_date_ms": "1500973879000",
          "purchase_date_pst": "2017-07-25 02:11:19 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-25 09:16:19 Etc/GMT",
          "expires_date_ms": "1500974179000",
          "expires_date_pst": "2017-07-25 02:16:19 America/Los_Angeles",
          "web_order_line_item_id": "1000000035725139",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318413351",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-25 09:16:19 Etc/GMT",
          "purchase_date_ms": "1500974179000",
          "purchase_date_pst": "2017-07-25 02:16:19 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-25 09:21:19 Etc/GMT",
          "expires_date_ms": "1500974479000",
          "expires_date_pst": "2017-07-25 02:21:19 America/Los_Angeles",
          "web_order_line_item_id": "1000000035725196",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318417975",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-25 09:23:30 Etc/GMT",
          "purchase_date_ms": "1500974610000",
          "purchase_date_pst": "2017-07-25 02:23:30 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-25 09:28:30 Etc/GMT",
          "expires_date_ms": "1500974910000",
          "expires_date_pst": "2017-07-25 02:28:30 America/Los_Angeles",
          "web_order_line_item_id": "1000000035725250",
          "is_trial_period": "false"
        },
        {
          "quantity": "1",
          "product_id": "testproduct",
          "transaction_id": "1000000318420598",
          "original_transaction_id": "1000000318012065",
          "purchase_date": "2017-07-25 09:28:30 Etc/GMT",
          "purchase_date_ms": "1500974910000",
          "purchase_date_pst": "2017-07-25 02:28:30 America/Los_Angeles",
          "original_purchase_date": "2017-07-24 08:13:25 Etc/GMT",
          "original_purchase_date_ms": "1500884005000",
          "original_purchase_date_pst": "2017-07-24 01:13:25 America/Los_Angeles",
          "expires_date": "2017-07-25 09:33:30 Etc/GMT",
          "expires_date_ms": "1500975210000",
          "expires_date_pst": "2017-07-25 02:33:30 America/Los_Angeles",
          "web_order_line_item_id": "1000000035725368",
          "is_trial_period": "false"
        }
      ],
      "latest_receipt": "DUMMY_RECEIPT:_A_BASE64_ENCODED_RECEIPT_DATA_WILL_BE_HERE",
      "pending_renewal_info": [
        {
          "expiration_intent": "1",
          "auto_renew_product_id": "testproduct",
          "is_in_billing_retry_period": "0",
          "product_id": "testproduct",
          "auto_renew_status": "0"
        }
      ]
    }''')


@pytest.fixture(scope='session')
def itunes_autorenew_response3():
    """Contributed by François Dupayrat @FrancoisDupayrat"""
    return json.loads(r'''{
      "auto_renew_status": 1,
      "status": 0,
      "auto_renew_product_id": "******************************",
      "receipt":{
        "original_purchase_date_pst":"2017-06-28 07:31:51 America/Los_Angeles",
        "unique_identifier":"******************************",
        "original_transaction_id":"******************************",
        "expires_date":"1506524970000",
        "transaction_id":"******************************",
        "quantity":"1",
        "product_id":"******************************",
        "item_id":"******************************",
        "bid":"******************************",
        "unique_vendor_identifier":"******************************",
        "web_order_line_item_id":"******************************",
        "bvrs":"1.1.6",
        "expires_date_formatted":"2017-09-27 15:09:30 Etc/GMT",
        "purchase_date":"2017-09-27 15:04:30 Etc/GMT",
        "purchase_date_ms":"1506524670000",
        "expires_date_formatted_pst":"2017-09-27 08:09:30 America/Los_Angeles",
        "purchase_date_pst":"2017-09-27 08:04:30 America/Los_Angeles",
        "original_purchase_date":"2017-06-28 14:31:51 Etc/GMT",
        "original_purchase_date_ms":"1498660311000"
      },
      "latest_receipt_info":{
        "original_purchase_date_pst":"2017-06-28 07:31:51 America/Los_Angeles",
        "unique_identifier":"******************************",
        "original_transaction_id":"******************************",
        "expires_date":"******************************",
        "transaction_id":"******************************",
        "quantity":"1",
        "product_id":"******************************",
        "item_id":"******************************",
        "bid":"******************************",
        "unique_vendor_identifier":"******************************",
        "web_order_line_item_id":"******************************",
        "bvrs":"1.1.6",
        "expires_date_formatted":"2017-09-27 15:09:30 Etc/GMT",
        "purchase_date":"2017-09-27 15:04:30 Etc/GMT",
        "purchase_date_ms":"1506524670000",
        "expires_date_formatted_pst":"2017-09-27 08:09:30 America/Los_Angeles",
        "purchase_date_pst":"2017-09-27 08:04:30 America/Los_Angeles",
        "original_purchase_date":"2017-06-28 14:31:51 Etc/GMT",
        "original_purchase_date_ms":"1498660311000"
      },
      "latest_receipt":"******************************"
    }''')


@pytest.fixture(params=[
    lazy_fixture('itunes_autorenew_response1'),
    lazy_fixture('itunes_autorenew_response2'),
    lazy_fixture('itunes_autorenew_response3'),
])
def itunes_autorenew_response(request):
    return request.param
