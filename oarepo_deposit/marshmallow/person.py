# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from flask import current_app
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import validates_schema, ValidationError, Schema, post_load, post_dump, fields, validates

from oarepo_deposit.marshmallow.common import clean_empty
from oarepo_deposit.marshmallow.identifier import PersistentId


class PersonSchemaV1(StrictKeysMixin, Schema):
    """Schema for a person."""
    familyname = SanitizedUnicode()
    givennames = SanitizedUnicode()
    name = SanitizedUnicode(required=True)
    affiliation = SanitizedUnicode()
    gnd = PersistentId(scheme='GND')
    orcid = PersistentId(scheme='ORCID')

    @post_dump(pass_many=False)
    @post_load(pass_many=False)
    def clean(self, data, **kwargs):
        """Clean empty values."""
        return clean_empty(data, ['orcid', 'gnd', 'affiliation'])

    @post_load(pass_many=False)
    def remove_gnd_prefix(self, data, **kwargs):
        """Remove GND prefix (which idutils normalization adds)."""
        gnd = data.get('gnd')
        if gnd and gnd.startswith('gnd:'):
            data['gnd'] = gnd[len('gnd:'):]

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate schema."""
        name = data.get('name')
        if not name:
            raise ValidationError(
                'Name is required.',
                field_names=['name']
            )


class ContributorSchemaV1(PersonSchemaV1):
    """Schema for a contributor."""

    type = fields.Str(required=True)

    @validates('type')
    def validate_type(self, value, **kwargs):
        """Validate the type."""
        if value not in \
            current_app.config['OAREPO_DEPOSIT_CONTRIBUTOR_DATACITE2MARC']:
            raise ValidationError(
                'Invalid contributor type.',
                field_names=['type']
            )
