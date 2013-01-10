
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='itunes-iap',
    version=__import__('itunesiap').__version__,
    description='Itunes In-app purchase validation api.',
    long_description=open('README.md').read(),
    author='Jeong YunWon',
    author_email='itunesiap@youknowone.org',
    url='https://github.com/youknowone/itunes-iap',
    packages=(
        'itunesiap',
    ),
    install_requires=[
        'requests',
    ],
)
