import six


def force_unicode(value):
    if not isinstance(value, six.string_types):
        return six.text_type(value)
    try:
        return value.decode('utf-8')
    except (AttributeError, UnicodeEncodeError):
        return value


def force_bytes(value):
    if not isinstance(value, six.string_types):
        value = force_unicode(value)
    try:
        return value.encode('utf-8')
    except (AttributeError, UnicodeDecodeError):
        return value
