# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from invenio_records_rest.schemas import StrictKeysMixin
from marshmallow import missing, ValidationError, fields
from six import string_types

from oarepo_deposit.models import AccessRight


class ResourceTypeMixin(object):
    """Schema for resource type."""

    resource_type = fields.Method('dump_resource_type', 'load_resource_type')

    def load_resource_type(self, data):
        """Split the resource type and into seperate keys."""
        if not isinstance(data, string_types):
            raise ValidationError(
                'Not a string.', field_names=['resource_type'])

        serialized_object = {}
        split_data = data.split('-')
        if len(split_data) == 2:
            serialized_object['type'], serialized_object['subtype'] = \
                split_data
        else:
            serialized_object['type'] = split_data[0]
        return serialized_object

    def dump_resource_type(self, data):
        """Dump resource type metadata."""
        resource_type = data.get('resource_type')
        if resource_type:
            if resource_type.get('subtype'):
                return resource_type['type'] + '-' + resource_type['subtype']
            else:
                return resource_type['type']
        else:
            return missing


class ResourceTypeSchema(StrictKeysMixin):
    """Resource type schema."""

    type = fields.Str(
        required=True,
        error_messages=dict(
            required=_('Type must be specified.')
        ),
    )
    subtype = fields.Str()
    openaire_subtype = fields.Str()

    def dump_openaire_type(self, obj):
        """Get OpenAIRE subtype."""
        acc = obj.get('access_right')
        if acc:
            return AccessRight.as_category(acc)
        return missing
