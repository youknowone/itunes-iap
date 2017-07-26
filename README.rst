itunes-iap v2
~~~~~~~~~~~~~

.. image:: https://travis-ci.org/youknowone/itunes-iap.svg?branch=master
    :target: https://travis-ci.org/youknowone/itunes-iap
.. image:: https://coveralls.io/repos/github/youknowone/itunes-iap/badge.svg?branch=master
    :target: https://coveralls.io/github/youknowone/itunes-iap?branch=master

- Source code: `<https://github.com/youknowone/itunes-iap>`_
- Documentation: `<http://itunes-iap.readthedocs.io/>`_
- Distribution: `<https://pypi.python.org/pypi/itunes-iap/>`_


The quick example
-----------------

Create request to create a request to itunes verifying api.

.. sourcecode:: python

   >>> import itunesiap
   >>> try:
   >>>     response = itunesiap.verify(raw_data)  # base64-encoded data
   >>> except itunesiap.exc.InvalidReceipt as e:
   >>>     print('invalid receipt')
   >>> print response.receipt.last_in_app.product_id  # other values are also available as property!

Practically useful attributes are:
    `product_id`, `original_transaction_id`, `quantity` and `unique_identifier`.

See the full document in:
    - :func:`itunesiap.verify`: The verifying function.
    - :class:`itunesiap.receipt.InApp`: The receipt object.


Installation
------------

PyPI is the recommended way.

.. sourcecode:: shell

    $ pip install itunesiap

To browse versions and tarballs, visit:
    `<https://pypi.python.org/pypi/itunes-iap/>`_


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


Note for v1 users
-----------------

There was breaking changes between v1 and v2 APIs.

- Specify version `0.6.6` for latest v1 API when you don't need new APIs.
- Or use `import itunesiap.legacy as itunesiap` instead of `import itunesiap`. (`from itunesiap import xxx` to `from itunesiap.legacy import xxx`)


Contributors
------------

See https://github.com/youknowone/itunes-iap/graphs/contributors
