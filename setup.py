import codecs
import os
from setuptools import setup


def read(fname):
    return codecs.open(
        os.path.join(
            os.path.dirname(__file__), fname), encoding='utf-8').read()


setup_requires = [
    'pytest_runner',
    ]

install_requires = [
    'setuptools',
    ]

tests_require = [
    # See tox.ini
    'pytest >=2.8.3',
    ]

docs_require = [
    'Sphinx',
    ]

setup(
    name="diceware_list",
    version="2.0",  # also set version in __init__.py.
    author="Uli Fouquet",
    author_email="uli@gnufix.de",
    description=(
        "Generate diceware wordlists."),
    license="GPL 3.0",
    keywords="diceware wordlist passphrase",
    url="https://github.com/ulif/diceware-list",
    py_modules=['diceware_list', 'libwordlist', 'wlflakes'],
    packages=[],
    namespace_packages=[],
    long_description=read('README.rst') + '\n\n\n' + read('CHANGES.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Topic :: Utilities",
        "Topic :: Security :: Cryptography",
        (
            "License :: OSI Approved :: "
            "GNU General Public License v3 or later (GPLv3+)"),
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    include_package_data=True,
    zip_safe=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=dict(
        docs=docs_require,
        ),
    entry_points={
        'console_scripts': [
            'diceware-list = diceware_list:main',
            'wlflakes = diceware_list.wlflakes:main',
            'wldownload = diceware_list.wldownload:main',
        ],
    },
)
