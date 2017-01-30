
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
    """Pretty interface for decoded receipt object.
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
                    if key not in self.__WHITELIST__:
                        warnings.warn('Given key `{0}` is not in __WHITELIST__. It maybe a wrong key. Check raw data `_` for real receipt data.'.format(key))
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

    status: See https://developer.apple.com/library/ios/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html#//apple_ref/doc/uid/TP40010573-CH104-SW1
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
    __WHITELIST__ = ['in_app']
    __EXPORT_FILTERS__ = {}

    @lazy_property
    def in_app(self):
        if 'in_app' in self._:
            return list(map(InApp, self._in_app))
        else:
            return [InApp(self._)]

    @property
    def last_in_app(self):
        return self.in_app[-1]


class InApp(ObjectMapper):
    __WHITELIST__ = [
        'quantity', 'product_id', 'transaction_id', 'original_transaction_id', 'is_trial_period',
        'purchase_date', 'original_purchase_date', 'expires_date', 'cancellation_date',
        'purchase_date_ms', 'original_purchase_date_ms', 'expires_date_ms', 'cancellation_date_ms', 'expires_date_formatted', ]
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
