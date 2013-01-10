from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_readme():
    try:
        with open('README.md') as f:
            return f.read().strip()
    except IOError:
        return ''


setup(
    name='itunes-iap',
    version=__import__('itunesiap').__version__,
    description='Itunes In-app purchase validation api.',
    long_description=get_readme(),
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
