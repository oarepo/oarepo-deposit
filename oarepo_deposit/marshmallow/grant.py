# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import fields


class FunderSchemaV1(StrictKeysMixin):
    """Schema for a funder."""

    doi = fields.Str()
    name = fields.Str(dump_only=True)
    acronyms = fields.List(fields.Str(), dump_only=True)


class GrantSchemaV1(StrictKeysMixin):
    """Schema for a grant."""

    title = SanitizedUnicode(dump_only=True)
    code = fields.Str()
    program = SanitizedUnicode(dump_only=True)
    acronym = fields.Str(dump_only=True)
    funder = fields.Nested(FunderSchemaV1)
