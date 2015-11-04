
from . import core
from . import exceptions


def verify(data, test_paid=lambda id: id, **kwargs):
    """Convinient verification shortcut.

    :param data: Itunes receipt data
    :param test_paid: Function to test the recept is paid. Function should
        raise error to disallow response. Parameter is `original_transaction_id`
    :return: :class:`itunesiap.core.Response`
    """
    request = core.Request(data, **kwargs)
    response = request.verify()
    test_paid(response.original_transaction_id)
    return response
