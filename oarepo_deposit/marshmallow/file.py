# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import Schema, fields


class FilesSchema(Schema):
    """Files metadata schema."""

    type = fields.String()
    checksum = fields.String()
    size = fields.Integer()
    bucket = fields.UUID()
    key = SanitizedUnicode()
    previewer = fields.Str()
    file_id = fields.UUID()
    version_id = fields.UUID()
