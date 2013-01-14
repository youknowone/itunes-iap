itunes-iap
~~~~~~~~~~

Quick example
-------------

    from itunesiap import Request
    request = Request(raw_data) # base64-encoded data
    receipt = request.validate()
    print receipt.product_id # any other values are available as property!

Practical useful values are: product_id, original_transaction_id, quantity, unique_identifier


Validation policy
-----------------

    from itunsiap import Request, set_validation_mode
    set_validation_mode('review') # enable both production and sandbox for appstore review. 'production', 'sandbox' or 'review'
    receipt = Request(raw_data).validate()
