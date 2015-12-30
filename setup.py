import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

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
    name="wordlist_gen",
    version="0.1.dev0",
    author="Uli Fouquet",
    author_email="uli@gnufix.de",
    description=(
        "Generate diceware wordlists."),
    license="GPL 3.0",
    keywords="diceware wordlist passphrase",
    url="https://github.com/ulif/wordlist-gen",
    py_modules=['wordlist_gen', ],
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=dict(
        tests=tests_require,
        docs=docs_require,
        ),
    entry_points={
        'console_scripts': [
            'wordlist_gen = wordlist_gen:main',
        ],
    },
)
