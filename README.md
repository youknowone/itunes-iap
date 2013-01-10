itunes-iap
====

Quick example
----

    from itunesiap import Request
    request = Request(raw_data) # base64-encoded data
    receipt = request.validate()
    print receipt.product_id

Validation policy
----

    from itunsiap import Request, set_validation_mode
    set_validation_mode('review') # enable both production and sandbox for appstore review. 'production', 'sandbox' or 'review'
    receipt = Request(raw_data).validate()