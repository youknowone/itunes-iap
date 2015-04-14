itunes-iap
~~~~~~~~~~

Quick example
-------------

Create request to create a request to itunes verify api.

    >>> from itunesiap import Request, InvalidReceipt
    >>> request = Request(raw_data) # base64-encoded data
    >>> try:
    >>>     receipt = request.verify()
    >>> except InvalidReceipt as e:
    >>>     print 'invalid receipt'
    >>> print receipt.product_id # any other values are available as property!

Practical useful values are: product_id, original_transaction_id, quantity, unique_identifier

Quick example with password (Apple Shared Secret)
-------------

Create request to create a request to itunes verify api.

    >>> from itunesiap import Request, InvalidReceipt
    >>> request = Request(raw_data, password) # base64-encoded data
    >>> try:
    >>>     receipt = request.verify()
    >>> except InvalidReceipt as e:
    >>>     print 'invalid receipt'
    >>> print receipt.product_id # any other values are available as property!
    >>> print receipt.latest_receipt # Get the latest receipt returned by Apple


Verification policy
-------------------

Set verification mode for production or sandbox api. Review mode also available for appstore review.

    >>> from itunesiap import Request
    >>> request = Request(raw_data)
    >>> with request.verification_mode('review'): # enable both production and sandbox for appstore review. 'production', 'sandbox' or 'review'
    >>>     receipt = request.verify()

Workflow Shortcut
-----------------

    >>> def test_paid(original_transaction_id):
    >>>     if db.contains(original_transaction_id):
    >>>         raise CustomException # custom exception
    >>>
    >>> import itunesiap
    >>> try:
    >>>     response = itunesiap.verify(raw_data, test_paid)
    >>> except itunesiap.RequestError:
    >>>     pass
    >>> except CustomException:
    >>>     pass
    >>> # response is instance of `itunesiap.core.Response`


Password support is merged from https://github.com/sportsy/itunes-iap
