from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    with open('itunesiap/version.txt') as f:
        return f.read().strip()


def get_readme():
    try:
        with open('README.rst') as f:
            return f.read().strip()
    except IOError:
        return ''


setup(
    name='itunes-iap',
    version=get_version(),
    description='Itunes In-app purchase validation api.',
    long_description=get_readme(),
    author='Jeong YunWon',
    author_email='itunesiap@youknowone.org',
    url='https://github.com/youknowone/itunes-iap',
    packages=(
        'itunesiap',
    ),
    package_data={
        'itunesiap': ['version.txt']
    },
    install_requires=[
        'distribute', 'requests', 'prettyexc>=0.4.1',
    ],
)
