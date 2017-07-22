""":mod:`itunesiap.receipt`

A successful response returns a JSON object including receipts. To manipulate
them in convinient way, `itunes-iap` wrapped it with :class:`ObjectMapper`.
"""
import pytz
import dateutil.parser
import warnings
import json

from .exceptions import MissingFieldError
from .tools import lazy_property


def _to_datetime(value):
    """Try to parse Apple iTunes receipt date format.

    By reference, they insists it is rfc3339:

        https://developer.apple.com/library/ios/releasenotes/General/ValidateAppStoreReceipt/Chapters/ReceiptFields.html#//apple_ref/doc/uid/TP40010573-CH106-SW4

    Though data I got from apple server does not. So the strategy is:

        - Give them a chance anyway.
        - Or split timezone string and read it from pytz.
    """
    try:
        d = dateutil.parser.parse(value)
    except ValueError as e:
        value, timezone = value.rsplit(' ', 1)
        try:
            d = dateutil.parser.parse(value + '+00:00')
        except ValueError:
            raise e
        d = d.replace(tzinfo=pytz.timezone(timezone))
    return d


def _to_bool(data):
    assert data in ('true', 'false'), \
        ("Cannot convert {0}, "
         "acceptable values are true' and 'false'".format(data))
    return json.loads(data)


class ObjectMapper(object):
    """A pretty interface for decoded receipt object.

    `__WHITELIST__` is a managed list of names. They are regarded as safe
    values and guaranteed to be converted in python representation when needed.
    `__EXPORT_FILTERS__` decides how to convert raw data to python
    representation.

    To access to the converted value, use a dictionary key as an attribute name.
    For example, the key `receipt` is accessible by:

    .. sourcecode:: python

        >>> mapper.receipt  # return converted python object Receipt
        >>> # == Receipt(mapper._['receipt'])

    To access to the raw JSON value, use a dictionary key as an attribute name
    but with the prefix `_`. For example, the key `receipt` is accessible by:

        >>> mapper._receipt  # return converted python object Receipt
        >>> # == mapper._['receipt']

    :param dict data: A JSON object.
    :return: :class:`ObjectMapper`
    """
    __WHITELIST__ = []
    __EXPORT_FILTERS__ = {}

    def __init__(self, data):
        self._ = data

    def __repr__(self):
        return u'<{0}({1})>'.format(self.__class__.__name__, self._)

    def __getitem__(self, item):
        return self._[item]

    def __getattr__(self, item):
        try:
            return super(ObjectMapper, self).__getattr__(item)
        except AttributeError:
            try:
                if item.startswith('_'):
                    key = item[1:]
                    if key not in self.__WHITELIST__:  # pragma: no cover
                        warnings.warn(
                            'Given key `{0}` is not in __WHITELIST__. It maybe a wrong key. Check raw data `_` for real receipt data.'.format(key))
                    return self._[key]
                if item in self.__EXPORT_FILTERS__:
                    filter = self.__EXPORT_FILTERS__[item]
                    return filter(self._[item])
                if item in self.__WHITELIST__:
                    return self._[item]
            except KeyError:
                raise MissingFieldError(item)
            return super(ObjectMapper, self).__getattribute__(item)


class Response(ObjectMapper):
    """The root response.

    About the value of status:
        - See https://developer.apple.com/library/ios/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html#//apple_ref/doc/uid/TP40010573-CH104-SW1
    """
    __WHITELIST__ = ['receipt', 'latest_receipt']  # latest_receipt_info
    __EXPORT_FILTERS__ = {'status': int}

    @lazy_property
    def receipt(self):
        return Receipt(self._receipt)

    @lazy_property
    def latest_receipt(self):
        return Receipt(self._latest_receipt)


class Receipt(ObjectMapper):
    """The actual receipt.

    The receipt may hold only one purchase directly in receipt object or may
    hold multiple purchases in `in_app` key.
    This object encapsulate it to list of :class:`InApp` object in `in_app`
    property.
    """
    __WHITELIST__ = ['in_app']
    __EXPORT_FILTERS__ = {}

    @lazy_property
    def in_app(self):
        """The list of purchases. If the receipt has receipt keys in the
        receipt body, it still will be wrapped as an :class:`InApp` and consists
        of this property
        """
        if 'in_app' in self._:
            return list(map(InApp, self._in_app))
        else:
            return [InApp(self._)]

    @property
    def last_in_app(self):
        """The last item in `in_app` property order by purchase_date."""
        return sorted(
            self.in_app, key=lambda x: x['original_purchase_date_ms'])[-1]


class InApp(ObjectMapper):
    """The individual purchases.

    The major keys are `unique_identifier`, `quantity`, `product_id` and
    `transaction_id`. `quantty` and `product_id` mean what kind of product and
    and how many of them the customer bought. `unique_identifier` and
    `transaction_id` is used to check where it is processed and track related
    purchases.

    For the detail, see also Apple docs.

    Any `date` related keys will be converted to python
    :class:`datetime.datetime` object. The quantity and any `date_ms` related
    keys will be converted to python :class:`int`.
    """
    __WHITELIST__ = [
        'unique_identifier', 'quantity', 'product_id', 'transaction_id',
        'original_transaction_id', 'is_trial_period',
        'purchase_date', 'original_purchase_date',
        'expires_date', 'cancellation_date',
        'purchase_date_ms', 'original_purchase_date_ms', 'expires_date_ms',
        'cancellation_date_ms', 'expires_date_formatted', ]
    __EXPORT_FILTERS__ = {
        'quantity': int,
        'is_trial_period': _to_bool,
        'purchase_date': _to_datetime,
        'original_purchase_date': _to_datetime,
        'expires_date': _to_datetime,
        'expires_date_formatted': _to_datetime,
        'cancellation_date': _to_datetime,
        'purchase_date_ms': int,
        'original_purchase_date_ms': int,
        'expires_date_ms': int,
        'cancellation_date_ms': int,
    }
