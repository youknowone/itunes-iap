
import itunesiap
import pytest


@pytest.fixture(scope='session')
def raw_receipt_legacy():
    return '''ewoJInNpZ25hdHVyZSIgPSAiQW1vSjJDNFhra1hXcngwbDBwMUVCMkhqdndWRkJPN3NxaHRPYVpYWXNtd29PblU4dkNYNWZJWFV6SmpwWVpwVGJ1bTJhWW5kci9uOHlBc2czUXc0WUZHMUtCbEpLSjU2c1gzcEpmWTRZd2hEMmJsdm1lZVowZ0FXKzNiajBRWGVjUWJORTk5b2duK09janY2U3dFSEdpdkRIY0FRNzBiMTYxekdpbTk2WHVKTkFBQURWekNDQTFNd2dnSTdvQU1DQVFJQ0NHVVVrVTNaV0FTMU1BMEdDU3FHU0liM0RRRUJCUVVBTUg4eEN6QUpCZ05WQkFZVEFsVlRNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURXpNREVHQTFVRUF3d3FRWEJ3YkdVZ2FWUjFibVZ6SUZOMGIzSmxJRU5sY25ScFptbGpZWFJwYjI0Z1FYVjBhRzl5YVhSNU1CNFhEVEE1TURZeE5USXlNRFUxTmxvWERURTBNRFl4TkRJeU1EVTFObG93WkRFak1DRUdBMVVFQXd3YVVIVnlZMmhoYzJWU1pXTmxhWEIwUTJWeWRHbG1hV05oZEdVeEd6QVpCZ05WQkFzTUVrRndjR3hsSUdsVWRXNWxjeUJUZEc5eVpURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd2daOHdEUVlKS29aSWh2Y05BUUVCQlFBRGdZMEFNSUdKQW9HQkFNclJqRjJjdDRJclNkaVRDaGFJMGc4cHd2L2NtSHM4cC9Sd1YvcnQvOTFYS1ZoTmw0WElCaW1LalFRTmZnSHNEczZ5anUrK0RyS0pFN3VLc3BoTWRkS1lmRkU1ckdYc0FkQkVqQndSSXhleFRldngzSExFRkdBdDFtb0t4NTA5ZGh4dGlJZERnSnYyWWFWczQ5QjB1SnZOZHk2U01xTk5MSHNETHpEUzlvWkhBZ01CQUFHamNqQndNQXdHQTFVZEV3RUIvd1FDTUFBd0h3WURWUjBqQkJnd0ZvQVVOaDNvNHAyQzBnRVl0VEpyRHRkREM1RllRem93RGdZRFZSMFBBUUgvQkFRREFnZUFNQjBHQTFVZERnUVdCQlNwZzRQeUdVakZQaEpYQ0JUTXphTittVjhrOVRBUUJnb3Foa2lHOTJOa0JnVUJCQUlGQURBTkJna3Foa2lHOXcwQkFRVUZBQU9DQVFFQUVhU2JQanRtTjRDL0lCM1FFcEszMlJ4YWNDRFhkVlhBZVZSZVM1RmFaeGMrdDg4cFFQOTNCaUF4dmRXLzNlVFNNR1k1RmJlQVlMM2V0cVA1Z204d3JGb2pYMGlreVZSU3RRKy9BUTBLRWp0cUIwN2tMczlRVWU4Y3pSOFVHZmRNMUV1bVYvVWd2RGQ0TndOWXhMUU1nNFdUUWZna1FRVnk4R1had1ZIZ2JFL1VDNlk3MDUzcEdYQms1MU5QTTN3b3hoZDNnU1JMdlhqK2xvSHNTdGNURXFlOXBCRHBtRzUrc2s0dHcrR0szR01lRU41LytlMVFUOW5wL0tsMW5qK2FCdzdDMHhzeTBiRm5hQWQxY1NTNnhkb3J5L0NVdk02Z3RLc21uT09kcVRlc2JwMGJzOHNuNldxczBDOWRnY3hSSHVPTVoydG04bnBMVW03YXJnT1N6UT09IjsKCSJwdXJjaGFzZS1pbmZvIiA9ICJld29KSW05eWFXZHBibUZzTFhCMWNtTm9ZWE5sTFdSaGRHVXRjSE4wSWlBOUlDSXlNREV5TFRBNUxUSXdJREU0T2pNeE9qTTRJRUZ0WlhKcFkyRXZURzl6WDBGdVoyVnNaWE1pT3dvSkluVnVhWEYxWlMxcFpHVnVkR2xtYVdWeUlpQTlJQ0kwTW1NeFlqTmtORFUxTmpNNE1qQmtaRGxoTlRsak56bGhOelUyTkRFd01ERm1ZemcxWlRNNUlqc0tDU0p2Y21sbmFXNWhiQzEwY21GdWMyRmpkR2x2YmkxcFpDSWdQU0FpTVRBd01EQXdNREExTmpFMk1UYzJOQ0k3Q2draVluWnljeUlnUFNBaU1TNHdJanNLQ1NKMGNtRnVjMkZqZEdsdmJpMXBaQ0lnUFNBaU1UQXdNREF3TURBMU5qRTJNVGMyTkNJN0Nna2ljWFZoYm5ScGRIa2lJRDBnSWpFaU93b0pJbTl5YVdkcGJtRnNMWEIxY21Ob1lYTmxMV1JoZEdVdGJYTWlJRDBnSWpFek5EZ3hPVEV3T1RneE9USWlPd29KSW5CeWIyUjFZM1F0YVdRaUlEMGdJa0poZEhSc1pVZHZiR1ExTUNJN0Nna2lhWFJsYlMxcFpDSWdQU0FpTlRVME5EazVNekExSWpzS0NTSmlhV1FpSUQwZ0ltTnZiUzUyWVc1cGJHeGhZbkpsWlhwbExtbG5kVzVpWVhSMGJHVWlPd29KSW5CMWNtTm9ZWE5sTFdSaGRHVXRiWE1pSUQwZ0lqRXpORGd4T1RFd09UZ3hPVElpT3dvSkluQjFjbU5vWVhObExXUmhkR1VpSUQwZ0lqSXdNVEl0TURrdE1qRWdNREU2TXpFNk16Z2dSWFJqTDBkTlZDSTdDZ2tpY0hWeVkyaGhjMlV0WkdGMFpTMXdjM1FpSUQwZ0lqSXdNVEl0TURrdE1qQWdNVGc2TXpFNk16Z2dRVzFsY21sallTOU1iM05mUVc1blpXeGxjeUk3Q2draWIzSnBaMmx1WVd3dGNIVnlZMmhoYzJVdFpHRjBaU0lnUFNBaU1qQXhNaTB3T1MweU1TQXdNVG96TVRvek9DQkZkR012UjAxVUlqc0tmUT09IjsKCSJlbnZpcm9ubWVudCIgPSAiU2FuZGJveCI7CgkicG9kIiA9ICIxMDAiOwoJInNpZ25pbmctc3RhdHVzIiA9ICIwIjsKfQ=='''  # noqa


@pytest.fixture(scope='session')
def itunes_response_legacy(raw_receipt_legacy):
    return itunesiap.verify(raw_receipt_legacy, env=itunesiap.env.sandbox)._


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
def itunes_response():
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
