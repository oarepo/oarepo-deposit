# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import Schema, fields


class LicenseSchemaV1(Schema):
    """License metadata schema."""

    identifier = SanitizedUnicode(required=True)
    license = SanitizedUnicode(required=True)
    source = SanitizedUnicode()
    url = SanitizedUnicode()
