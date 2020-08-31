# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
import jsonref
from flask import current_app
from invenio_records import Record


def clean_empty(data, keys, **kwargs):
    """Clean empty values."""
    for k in keys:
        if k in data and not data[k]:
            del data[k]
    return data


class RefResolverMixin(object):
    """Mixin for helping to validate if a JSONRef resolves."""

    def validate_jsonref(self, value):
        """Validate that a JSONRef resolves.
        Test is skipped if not explicitly requested and you are in an
        application context.
        """
        if not self.context.get('replace_refs') or not current_app:
            return True

        if not (isinstance(value, dict) and '$ref' in value):
            return True

        try:
            Record(value).replace_refs().dumps()
            return True
        except jsonref.JsonRefError:
            return False
