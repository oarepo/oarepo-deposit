# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""

from datetime import datetime

import arrow
from flask import current_app
from flask_babelex import format_date
from invenio_records import Record
from invenio_search import RecordsSearch, current_search_client

# TODO: replace with translation function
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin

from oarepo_deposit.marshmallow.deposit import DepositRecordSchemaV1

_ = lambda x: x


class DepositRecord(SchemaKeepingRecordMixin,
                    MarshmallowValidatedRecordMixin,
                    Record):
    """Deposit record class."""
    MARSHMALLOW_SCHEMA = DepositRecordSchemaV1
    ALLOWED_SCHEMAS = ('deposit-v1.0.0.json',)
    PREFERRED_SCHEMA = 'deposit-v1.0.0.json'
    VALIDATE_MARSHMALLOW = True
    VALIDATE_PATCH = True
