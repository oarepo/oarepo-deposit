# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from __future__ import absolute_import, print_function, unicode_literals

import json

from flask import current_app
from invenio_db import db
from invenio_opendefinition.minters import license_minter
from invenio_opendefinition.resolvers import license_resolver
from invenio_opendefinition.validators import license_validator
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.api import Record
from pkg_resources import resource_string


def read_json(path):
    """Retrieve JSON from package resource."""
    return json.loads(
        resource_string('oarepo_deposit', path).decode('utf8'))


def update_legacy_meta(license):
    """Update the Zenodo legacy terms for license metadata.
    Updates the metadata in order to conform with opendefinition schema.
    """
    l = dict(license)
    if 'od_conformance' not in l:
        l['od_conformance'] = 'approved' if l['is_okd_compliant'] \
            else 'rejected'
    if 'osd_conformance' not in l:
        l['osd_conformance'] = 'approved' if l['is_osi_compliant'] \
            else 'rejected'
    l.pop('is_okd_compliant', None)
    l.pop('is_osi_compliant', None)
    l['$schema'] = 'http://{0}{1}/{2}'.format(
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config['JSONSCHEMAS_ENDPOINT'],
        current_app.config['OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE']
    )
    return l


def create_new_license(license):
    """Create a new license record.

    :param license: License dictionary to be loaded.
    :type license: dict
    """
    license = update_legacy_meta(license)
    license_validator.validate(license)
    record = Record.create(license)
    license_minter(record.id, license)


def load_licenses():
    """Load licenses from a data file.

    Create extra PID if license is to be mapped and already exists, otherwise
    create a new license record and a PID.
    """
    data = read_json('data/licenses.json')
    map_ = read_json('data/licenses-map.json')
    mapped = [(d, map_[d['id']] if d['id'] in map_ else None) for d in data]
    try:
        for lic, alt_pid in mapped:
            if lic['id'] == alt_pid:  # Skip the already-existing licenses
                continue
            if alt_pid:
                try:
                    pid, record = license_resolver.resolve(alt_pid)
                    license_minter(record.id, lic)
                except PIDDoesNotExistError:
                    create_new_license(lic)
            else:
                create_new_license(lic)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
