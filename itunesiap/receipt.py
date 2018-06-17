""":mod:`itunesiap.receipt`

A successful response returns a JSON object including receipts. To manipulate
them in convinient way, `itunes-iap` wrapped it with :class:`ObjectMapper`.
"""
import datetime
import warnings
import pytz
import dateutil.parser
import json
from collections import defaultdict
from prettyexc import PrettyException

from .tools import lazy_property

__all__ = ('WARN_UNDOCUMENTED_FIELDS', 'Response', 'Receipt', 'InApp')


WARN_UNDOCUMENTED_FIELDS = True
WARN_UNLISTED_FIELDS = True

_warned_undocumented_fields = defaultdict(bool)
_warned_unlisted_field = defaultdict(bool)

'''
class ExpirationIntent(Enum):
    CustomerCanceledTheirSubscription = 1
    BillingError = 2
    CustumerDidNotAgreeToARecentPriceIncrease = 3
    ProductWasNotAvailableForPurchaseAtTheTimeOfRenewal = 4
    UnknownError = 5
'''


class MissingFieldError(PrettyException, AttributeError, KeyError):
    """A Backward compatibility error."""


def _rfc3339_to_datetime(value):
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


def _ms_to_datetime(value):
    nd = datetime.datetime.utcfromtimestamp(int(value) / 1000)
    ad = nd.replace(tzinfo=pytz.UTC)
    return ad


def _to_bool(data):
    assert data in ('true', 'false'), \
        ("Cannot convert {0}, "
         "acceptable values are true' and 'false'".format(data))
    return json.loads(data)


class ObjectMapper(object):
    """A pretty interface for decoded receipt object.

    `__DOCUMENTED_FIELDS__` and `__UNDOCUMENTED_FIELDS__` are managed lists of
    field names. They are regarded as safe values and guaranteed to be
    converted in python representation when needed.
    When a field exists in `__OPAQUE_FIELDS__`, its result will be redirected.
    The common type is :class:`str`.
    When a field exists in `__FIELD_ADAPTERS__`, it will be converted to
    corresponding python data representation.

    To access to the converted value, use a dictionary key as an attribute name.
    For example, the key `receipt` is accessible by:

    .. sourcecode:: python

        >>> mapper.receipt  # return converted python object Receipt
        >>> # == Receipt(mapper['receipt'])

    To access to the raw JSON value, use a dictionary key as an attribute name
    but with the prefix `_`. For example, the key `receipt` is accessible by:

        >>> mapper._receipt  # return converted python object Receipt
        >>> # == mapper['receipt']

    :param dict data: A JSON object.
    :return: :class:`ObjectMapper`
    """
    __OPAQUE_FIELDS__ = frozenset([])
    __FIELD_ADAPTERS__ = {}
    __DOCUMENTED_FIELDS__ = frozenset([])
    __UNDOCUMENTED_FIELDS__ = frozenset([])

    def __init__(self, data):
        self._ = data

    def __repr__(self):
        return u'<{self.__class__.__name__}({self._})>'.format(self=self)

    def __getitem__(self, item):
        return self._[item]

    def __contains__(self, item):
        return item in self._

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            if name.startswith('_'):
                key = name[1:]
                if key in self.__DOCUMENTED_FIELDS__:
                    pass
                elif key in self.__UNDOCUMENTED_FIELDS__:
                    self.warn_undocumented(key)
                else:
                    self.warn_unlisted(key)
                try:
                    return self._[key]
                except KeyError:
                    raise MissingFieldError(name)

            if name in self.__DOCUMENTED_FIELDS__:
                pass
            elif name in self.__UNDOCUMENTED_FIELDS__:
                self.warn_undocumented(name)
            else:
                self.warn_unlisted(name)

            if name in self.__OPAQUE_FIELDS__:
                def _get(_self):
                    try:
                        value = _self._[name]
                    except KeyError:
                        raise MissingFieldError(name)
                    return value
                setattr(self.__class__, name, property(_get))
            elif name in self.__FIELD_ADAPTERS__:
                adapter = self.__FIELD_ADAPTERS__[name]
                if isinstance(adapter, tuple):
                    data_key, transform = adapter
                else:
                    data_key = name
                    transform = adapter

                def _get(_self):
                    try:
                        value = _self._[data_key]
                    except KeyError:
                        raise MissingFieldError(name)
                    return transform(value)
                setattr(self.__class__, name, lazy_property(_get))
            else:
                pass  # unhandled. raise AttributeError
        return self.__getattribute__(name)

    @classmethod
    def from_list(cls, data_list):
        return [cls(data) for data in data_list]

    @staticmethod
    def warn_undocumented(name):
        if not WARN_UNDOCUMENTED_FIELDS or _warned_undocumented_fields[name]:
            return
        warnings.warn(
            "The given field '{name}' is an undocumented field. "
            "The behavior is neither documented nor guaranteed by Apple. "
            "To suppress further warnings, set the "
            "`itunesiap.receipt.WARN_UNDOCUMENTED_FIELDS` False"
            .format(name=name))
        _warned_undocumented_fields[name] = True

    @staticmethod
    def warn_unlisted(name):
        if not WARN_UNLISTED_FIELDS or _warned_unlisted_field[name]:
            return
        warnings.warn(
            "The given field '{name}' is an unlisted field. "
            "If the field actually exists, ignore this warning message. "
            "To suppress further warnings, please report it to itunes-iap "
            "project or set the `itunesiap.receipt.WARN_UNLISTED_FIELDS` "
            "False.".format(name=name))
        _warned_unlisted_field[name] = True


class Receipt(ObjectMapper):
    """The actual receipt.

    The receipt may hold only one purchase directly in receipt object or may
    hold multiple purchases in `in_app` key.
    This object encapsulate it to list of :class:`InApp` object in `in_app`
    property.

    :see: `<https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ReceiptFields.html>`_
    """
    __OPAQUE_FIELDS__ = frozenset([
        # app receipt fields
        'bundle_id',
        'application_version',
        'original_application_version',
        # in-app purchase receipt fields
        'product_id',
        'transaction_id',
        'original_transaction_id',
        'expires_date_formatted',
        'app_item_id',
        'version_external_identifier',
        'web_order_line_item_id',
        'auto_renew_product_id',
    ])
    __FIELD_ADAPTERS__ = {
        # app receipt fields
        'receipt_creation_date': _rfc3339_to_datetime,
        'receipt_creation_date_ms': int,
        'expiration_date': _rfc3339_to_datetime,
        'expiration_date_ms': int,
        # in-app purchase receipt fields
        'quantity': int,
        'purchase_date': _rfc3339_to_datetime,
        'purchase_date_ms': int,
        'original_purchase_date': _rfc3339_to_datetime,
        'original_purchase_date_ms': int,
        'expires_date': _ms_to_datetime,
        'expires_date_ms': ('expires_date', int),
        'expiration_intent': int,
        'is_in_billing_retry_period': _to_bool,
        'is_in_intro_offer_period': _to_bool,
        'cancellation_date': _rfc3339_to_datetime,
        'cancellation_reason': int,
        'auto_renew_status': int,
        'price_consent_status': int,
        'request_date': _rfc3339_to_datetime,
        'request_date_ms': int,
    }
    __DOCUMENTED_FIELDS__ = frozenset([
        # app receipt fields
        'bundle_id',
        'in_app',
        'application_version',
        'original_application_version',
        'receipt_creation_date',
        'expiration_date',
        # in-app purchase receipt fields
        'quantity',
        'product_id',
        'transaction_id',
        'original_transaction_id',
        'purchase_date',  # _formatted value
        'original_purchase_date',
        'expires_date',  # _ms value
        'is_in_billing_retry_period',
        'is_in_intro_offer_period',
        'cancellation_date',
        'cancellation_reason',
        'app_item_id',
        'version_external_identifier',
        'web_order_line_item_id',
        'auto_renew_status',
        'auto_renew_product_id',
        'price_consent_status',
    ])
    __UNDOCUMENTED_FIELDS__ = frozenset([
        # app receipt fields
        'request_date',
        'request_date_ms',
        'version_external_identifier',
        'receipt_creation_date_ms',
        'expiration_date_ms',
        # in-app purchase receipt fields
        'purchase_date_ms',
        'original_purchase_date_ms',
        'expires_date_formatted',
        'unique_identifier',
    ])

    @lazy_property
    def single_purchase(self):
        return Purchase(self._)

    @lazy_property
    def in_app(self):
        """The list of purchases. If the receipt has receipt keys in the
        receipt body, it still will be wrapped as an :class:`InApp` and consists
        of this property
        """
        if 'in_app' in self._:
            return list(map(InApp, self._in_app))
        else:
            return [self.single_purchase]

    @property
    def last_in_app(self):
        """The last item in `in_app` property order by purchase_date."""
        return sorted(
            self.in_app, key=lambda x: x['original_purchase_date_ms'])[-1]


class Purchase(ObjectMapper):
    """The individual purchases.

    The major keys are `quantity`, `product_id` and `transaction_id`.
    `quantty` and `product_id` mean what kind of product and
    and how many of them the customer bought. `unique_identifier` and
    `transaction_id` is used to check where it is processed and track related
    purchases.

    For the detail, see also Apple docs.

    Any `date` related keys will be converted to python
    :class:`datetime.datetime` object. The quantity and any `date_ms` related
    keys will be converted to python :class:`int`.
    """
    __OPAQUE_FIELDS__ = frozenset([
        'product_id',
        'transaction_id',
        'original_transaction_id',
        'web_order_line_item_id',
        'unique_identifier',
        'expires_date_formatted',
    ])
    __FIELD_ADAPTERS__ = {
        'quantity': int,
        'purchase_date': _rfc3339_to_datetime,
        'purchase_date_ms': int,
        'original_purchase_date': _rfc3339_to_datetime,
        'original_purchase_date_ms': int,
        'expires_date': _rfc3339_to_datetime,
        'expires_date_ms': int,
        'is_trial_period': _to_bool,
        'cancellation_date': _rfc3339_to_datetime,
        'cancellation_date_ms': int,
        'cancellation_reason': int,
    }
    __DOCUMENTED_FIELDS__ = frozenset([
        'quantity',
        'product_id',
        'transaction_id',
        'original_transaction_id',
        'purchase_date',
        'original_purchase_date',
        'expires_date',
        'is_trial_period',
        'cancellation_date',
        'cancellation_reason',
        'web_order_line_item_id',
    ])
    __UNDOCUMENTED_FIELDS__ = frozenset([
        'unique_identifier',
        'purchase_date_ms',
        'original_purchase_date_ms',
        'cancellation_date_ms',
        'expires_date_formatted',  # legacy receipts has this field as actual "expires_date"
    ])

    def __eq__(self, other):
        if not isinstance(other, Purchase):  # pragma: no cover
            return False
        return self._ == other._

    @lazy_property
    def expires_date(self):
        if 'expires_date_formatted' in self:
            return _rfc3339_to_datetime(self['expires_date_formatted'])
        try:
            value = self['expires_date']
        except KeyError:
            raise MissingFieldError('expires_date')
        try:
            int(value)
        except ValueError:
            return _rfc3339_to_datetime(value)
        else:
            return _ms_to_datetime(value)


class InApp(Purchase):
    pass


class PendingRenewalInfo(ObjectMapper):
    __OPAQUE_FIELDS__ = frozenset([
        'auto_renew_product_id',
    ])
    __FIELD_ADAPTERS__ = {
        'auto_renew_status': int,
        'expiration_intent': int,
        'is_in_billing_retry_period': int,
    }
    __DOCUMENTED_FIELDS__ = frozenset([
        'expiration_intent',
        'auto_renew_status',
        'auto_renew_product_id',
        'is_in_billing_retry_period',
    ])
    __UNDOCUMENTED_FIELDS__ = frozenset([
    ])


class Response(ObjectMapper):
    """The root response.

    About the value of status:
        - See https://developer.apple.com/library/ios/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html#//apple_ref/doc/uid/TP40010573-CH104-SW1
    """
    __OPAQUE_FIELDS__ = frozenset([
        'latest_receipt',
    ])
    __FIELD_ADAPTERS__ = {
        'status': int,
        'receipt': Receipt,
        'pending_renewal_info': PendingRenewalInfo.from_list,
    }
    __DOCUMENTED_FIELDS__ = frozenset([
        'status',
        'receipt',
        'latest_receipt',
        'latest_receipt_info',
        # 'latest_expired_receipt_info',
        'pending_renewal_info',
        # is-retryable
    ])
    __UNDOCUMENTED_FIELDS__ = frozenset([
    ])

    @lazy_property
    def latest_receipt_info(self):
        if 'latest_receipt_info' not in self:
            # not an auto-renew purchase
            raise MissingFieldError('latest_receipt_info')
        info = self['latest_receipt_info']
        if isinstance(info, dict):  # iOS6 style
            return Purchase(info)
        elif isinstance(info, list):  # iOS7 style
            return InApp.from_list(info)
        else:  # pragma: no cover
            assert False
