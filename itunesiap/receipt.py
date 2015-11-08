
import warnings
from .tools import lazy_property


class ObjectMapper(object):
    """Pretty interface for decoded receipt obejct.
    """
    __WHITELIST__ = []
    __EXPORT_FILTERS__ = {}

    def __init__(self, data):
        self._ = data

    def __repr__(self):
        return u'<{}({})>'.format(self.__class__.__name__, self._)

    def __getitem__(self, item):
        return self._[item]

    def __getattr__(self, item):
        try:
            return super(ObjectMapper, self).__getattr__(item)
        except AttributeError:
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
    __WHITELIST__ = ['quantity', 'product_id', 'transaction_id', 'original_transaction_id', 'purchase_date', 'original_purchase_date', 'expires_date', 'cancellation_date']
    __EXPORT_FILTERS__ = {
        'quantity': int,
    }
