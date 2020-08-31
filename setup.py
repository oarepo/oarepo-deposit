# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""" Common data model for OA repository records according to Zenodo deposit model"""

import os

from setuptools import find_packages, setup

OAREPO_VERSION = os.environ.get('OAREPO_VERSION', '3.2.1')

readme = open('README.md').read()
history = open('CHANGES.rst').read()

tests_require = [
]

extras_require = {
    'tests': [
        *tests_require,
        'oarepo[tests]~={version}'.format(
            version=OAREPO_VERSION)],
    'tests-es7': [
        *tests_require,
        'oarepo[tests-es7]~={version}'.format(
            version=OAREPO_VERSION)],
    'validate': [
        'oarepo-validate'
    ]
}


extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'idutils',
    'pycountry',
    'oarepo-multilingual',
    'invenio-opendefinition'
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('oarepo_deposit', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='oarepo-deposit',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='oarepo deposit record data model',
    license='MIT',
    author='Miroslav Bauer @ CESNET',
    author_email='bauer@cesnet.cz',
    url='https://github.com/oarepo/oarepo-deposit',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_oarepo_mapping_includes': [
            'oarepo_deposit=oarepo_deposit.included_mappings'
        ],
        'invenio_jsonschemas.schemas': [
            'oarepo_deposit = oarepo_deposit.jsonschemas'
        ],
        'flask.commands': [
            'deposit = oarepo_deposit.cli:deposit',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Development Status :: 4 - Beta',
    ],
)
