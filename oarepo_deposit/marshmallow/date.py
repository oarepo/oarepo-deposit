# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from invenio_oarepo_multilingual.marshmallow import MultilingualStringSchemaV1
from invenio_records_rest.schemas.fields import DateString
from marshmallow import Schema, fields


class DateSchemaV1(Schema):
    """Schema for date intervals."""

    start = DateString()
    end = DateString()
    type = fields.Str(required=True)
    description = MultilingualStringSchemaV1()
