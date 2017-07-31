Quickstart
==========

Create request to create a request to itunes verify api.

.. sourcecode:: python

    >>> import itunesiap
    >>> try:
    >>>     response = itunesiap.verify(raw_data)  # base64-encoded data
    >>> except itunesiap.exc.InvalidReceipt as e:
    >>>     print('invalid receipt')
    >>> print response.receipt.last_in_app.product_id
    >>> # other values are also available as properties!

Practically useful attributes are: `product_id`, `original_transaction_id`, `quantity` and `unique_identifier`.
See the full document in :class:`itunesiap.receipt.InApp`.

For :mod:`asyncio`, replace :func:`itunesiap.verify` funciton to
:func:`itunesiap.aioverify`. That's all.

.. sourcecode:: python

    >>> response = itunesiap.aioverify(raw_data)


itunesiap.verify()
------------------
Note that most of the use cases are covered by the :func:`itunesiap.verify`
function.

.. autofunction:: itunesiap.verify

.. autofunction:: itunesiap.aioverify


Apple in-review mode
--------------------

In review mode, your actual users who use older versions want to verify in
production server but the reviewers in Apple office want to verify in sandbox
server.

Note: The default env is `production` mode which doesn't allow any sandbox
verifications.

You can change the verifying mode by specifying `env`.

.. sourcecode:: python

    >>> # review mode
    >>> itunesiap.verify(raw_data, env=itunesiap.env.review)
    >>> # sandbox mode
    >>> itunesiap.verify(raw_data, env=itunesiap.env.sandbox)

Also directly passing arguments are accepted:

.. sourcecode:: python

    >>> # review mode
    >>> itunesiap.verify(raw_data, use_production=True, use_sandbox=True)


Password for shared secret
--------------------------

When you have shared secret for your app, the verifying process requires a
shared secret password.

About the shared secret, See: In-App_Purchase_Configuration_Guide_.

.. sourcecode:: python

    >>> try:
    >>>     # Add password as a parameter
    >>>     response = itunesiap.verify(raw_data, password=password)
    >>> except itunesiap.exc.InvalidReceipt as e:
    >>>     print('invalid receipt')
    >>> in_app = response.receipt.last_in_app  # Get the latest receipt returned by Apple


.. _In-App_Purchase_Configuration_Guide: https://developer.apple.com/library/content/documentation/LanguagesUtilities/Conceptual/iTunesConnectInAppPurchase_Guide/Chapters/CreatingInAppPurchaseProducts.html