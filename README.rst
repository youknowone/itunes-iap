itunes-iap
~~~~~~~~~~

Quick example
-------------

Create request to create a request to itunes verify api.
    
    >>> from itunesiap import Request
    >>> request = Request(raw_data) # base64-encoded data
    >>> receipt = request.verify()
    >>> print receipt.product_id # any other values are available as property!

Practical useful values are: product_id, original_transaction_id, quantity, unique_identifier


Verification policy
-----------------

Set verification mode for production or sandbox api. Review mode also available for appstore review.

    >>> from itunsiap import Request, set_verification_mode
    >>> set_verification_mode('review') # enable both production and sandbox for appstore review. 'production', 'sandbox' or 'review'
    >>> receipt = Request(raw_data).verify()
