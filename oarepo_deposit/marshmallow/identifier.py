# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
import idutils
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import Schema, fields, pre_load, post_load, validates_schema, ValidationError, missing, validate

from oarepo_deposit.config import OAREPO_RELATION_TYPES
from oarepo_deposit.marshmallow.resource import ResourceTypeMixin

# TODO: replace with translation function
_ = lambda x: x


class DOIField(SanitizedUnicode):
    """Special DOI field."""

    default_error_messages = {
        'invalid_doi': _(
            'The provided DOI is invalid - it should look similar '
            ' to \'10.1234/foo.bar\'.'),
        'managed_prefix': (
            'The prefix {prefix} is administrated locally.'),
        'banned_prefix': (
            'The prefix {prefix} is invalid.'
        ),
        'required_doi': _(
            'The DOI cannot be changed.'
        ),
    }

    def __init__(self, required_doi=None, allowed_dois=None,
                 managed_prefixes=None, banned_prefixes=None, *args, **kwargs):
        """Initialize field."""
        super(DOIField, self).__init__(*args, **kwargs)
        self.required_doi = required_doi
        self.allowed_dois = allowed_dois
        self.managed_prefixes = managed_prefixes or []
        self.banned_prefixes = banned_prefixes or []

    def _deserialize(self, value, attr, data):
        """Deserialize DOI value."""
        value = super(DOIField, self)._deserialize(value, attr, data)
        value = value.strip()
        if value == '' and not (
            self.required or self.context.get('doi_required')):
            return value
        if not idutils.is_doi(value):
            self.fail('invalid_doi')
        return idutils.normalize_doi(value)

    def _validate(self, value):
        """Validate DOI value."""
        super(DOIField, self)._validate(value)

        required_doi = self.context.get(
            'required_doi', self.required_doi)
        allowed_dois = self.context.get(
            'allowed_dois', self.allowed_dois)
        managed_prefixes = self.context.get(
            'managed_prefixes', self.managed_prefixes)
        banned_prefixes = self.context.get(
            'banned_prefixes', self.banned_prefixes)

        # First check for required DOI.
        if required_doi:
            if value == required_doi:
                return
            self.fail('required_doi')
        # Check if DOI is in allowed list.
        if allowed_dois:
            if value in allowed_dois:
                return

        prefix = value.split('/')[0]
        # Check for managed prefix
        if managed_prefixes and prefix in managed_prefixes:
            self.fail('managed_prefix', prefix=prefix)
        # Check for banned prefixes
        if banned_prefixes and prefix in banned_prefixes:
            self.fail(
                'banned_prefix',
                prefix=prefix
            )


class PersistentId(SanitizedUnicode):
    """Special DOI field."""

    default_error_messages = {
        'invalid_scheme': 'Not a valid {scheme} identifier.',
        # TODO: Translation on format strings sounds tricky...
        # 'invalid_scheme': _('Not a valid {scheme} identifier.'),
        'invalid_pid': 'Not a valid persistent identifier.',
    }

    def __init__(self, scheme=None, normalize=True, *args, **kwargs):
        """Initialize field."""
        super(PersistentId, self).__init__(*args, **kwargs)
        self.scheme = scheme
        self.normalize = normalize

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize persistent identifier value."""
        if not value:
            return missing
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize persistent identifier value."""
        value = super(PersistentId, self)._deserialize(value, attr, data)
        value = value.strip()

        schemes = idutils.detect_identifier_schemes(value)
        if self.scheme and self.scheme.lower() not in schemes:
            self.fail('invalid_scheme', scheme=self.scheme)
        if not schemes:
            self.fail('invalid_pid')
        return idutils.normalize_pid(value, schemes[0]) \
            if self.normalize else value


class IdentifierSchemaV1(Schema, StrictKeysMixin):
    """Schema for a identifiers.
    During deserialization the schema takes care of detecting the identifier
    scheme if not specified, as well as validating and normalizing the
    persistent identifier value.
    """

    identifier = PersistentId(required=True)
    scheme = fields.Str()

    @pre_load()
    def detect_scheme(self, data):
        """Load scheme."""
        id_ = data.get('identifier')
        scheme = data.get('scheme')
        if not scheme and id_:
            scheme = idutils.detect_identifier_schemes(id_)
            if scheme:
                data['scheme'] = scheme[0]
        return data

    @post_load()
    def normalize_identifier(self, data):
        """Normalize identifier."""
        data['identifier'] = idutils.normalize_pid(
            data['identifier'], data['scheme'])

    @validates_schema
    def validate_data(self, data):
        """Validate identifier and scheme."""
        id_ = data.get('identifier')
        scheme = data.get('scheme')
        if not id_:
            raise ValidationError(
                'Identifier is required.',
                field_names=['identifier']
            )

        schemes = idutils.detect_identifier_schemes(id_)
        if not schemes:
            raise ValidationError(
                'Not a valid persistent identifier.',
                field_names=['identifier']
            )
        if scheme not in schemes:
            raise ValidationError(
                'Not a valid {0} identifier.'.format(scheme),
                field_names=['identifier']
            )


class AlternateIdentifierSchemaV1(IdentifierSchemaV1, ResourceTypeMixin):
    """Schema for an alternate identifier."""


class RelatedIdentifierSchemaV1(IdentifierSchemaV1, ResourceTypeMixin):
    """Schema for a related identifier."""

    relation = fields.Str(
        required=True,
        validate=validate.OneOf(
            choices=[x[0] for x in OAREPO_RELATION_TYPES],
        )
    )
