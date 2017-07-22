
"""
Test for deprecated methods to ensure they are not broken.
"""

import itunesiap


def test_context(raw_receipt_legacy):
    """Test sandbox receipts with real itunes server."""
    sandbox_receipt = raw_receipt_legacy
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
