from __future__ import with_statement
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_version():
    with open('itunesiap/version.txt') as f:
        return f.read().strip()


def get_readme():
    try:
        with open('README.rst') as f:
            return f.read().strip()
    except IOError:
        return ''


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


requirements = [
    'requests==2.7.0',
    'six==1.9.0',
    'prettyexc',
]

test_requirements = [
    'tox==2.1.1',
    'pytest==2.7.2',
    'vcrpy==1.7.3',
    'mock==1.3.0',
]


setup(
    name='itunes-iap',
    version=get_version(),
    description='Itunes In-app purchase verification api.',
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
    install_requires=requirements,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    tests_require=requirements + test_requirements,
    cmdclass={'test': Tox},
)
