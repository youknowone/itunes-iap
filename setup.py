import setuptools

assert tuple(map(int, setuptools.__version__.split('.'))) >= (39, 2, 0), 'Plesase upgrade setuptools by `pip install -U setuptools`'

setuptools.setup()
