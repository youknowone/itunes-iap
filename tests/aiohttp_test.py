import sys

if sys.version_info[:2] >= (3, 5):
    from .aiohttp_test_py35 import *  # noqa
else:
    import pytest

    @pytest.mark.skip
    def test_no_aiohttp_supported_version():
        pass
