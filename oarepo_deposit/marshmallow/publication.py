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
from oarepo_multilingual.marshmallow import MultilingualStringV2

from oarepo_deposit.marshmallow.person import PersonSchemaV1


class JournalSchemaV1(StrictKeysMixin):
    """Schema for a journal."""

    issue = SanitizedUnicode()
    pages = SanitizedUnicode()
    title = MultilingualStringV2()
    volume = SanitizedUnicode()
    year = SanitizedUnicode()


class ImprintSchemaV1(StrictKeysMixin):
    """Schema for imprint."""

    publisher = SanitizedUnicode()
    place = SanitizedUnicode()
    isbn = SanitizedUnicode()


class PartOfSchemaV1(StrictKeysMixin):
    """Schema for Part of Publication."""

    pages = fields.Str()
    title = MultilingualStringV2()


class ThesisSchemaV1(StrictKeysMixin):
    """Schema for thesis."""

    university = SanitizedUnicode()
    supervisors = fields.Nested(PersonSchemaV1, many=True)
