# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from invenio_records_rest.schemas.fields import SanitizedUnicode
from jsonschema import ValidationError
from marshmallow import Schema, fields, validates


class LocationSchemaV1(Schema):
    """Schema for geographical locations."""

    lat = fields.Float()
    lon = fields.Float()
    place = SanitizedUnicode(required=True)
    description = SanitizedUnicode()

    @validates('lat')
    def validate_latitude(self, value):
        """Validate that location exists."""
        if not (-90 <= value <= 90):
            raise ValidationError(
                _('Latitude must be between -90 and 90.')
            )

    @validates('lon')
    def validate_longitude(self, value):
        """Validate that location exists."""
        if not (-180 <= value <= 180):
            raise ValidationError(
                _('Longitude must be between -180 and 180.')
            )
