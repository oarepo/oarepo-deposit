# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from urllib.parse import quote

import arrow
import idutils
import pycountry
from flask import has_request_context, current_app
from invenio_oarepo_multilingual.marshmallow import MultilingualStringSchemaV1
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode, SanitizedHTML
from marshmallow import Schema, validate, fields, validates, ValidationError, validates_schema, missing, pre_load, \
    post_load, pre_dump
from werkzeug.routing import BuildError

from oarepo_deposit.marshmallow.common import RefResolverMixin
from oarepo_deposit.marshmallow.date import DateSchemaV1
from oarepo_deposit.marshmallow.identifier import DOIField, RelatedIdentifierSchemaV1, AlternateIdentifierSchemaV1
from oarepo_deposit.marshmallow.location import LocationSchemaV1
from oarepo_deposit.marshmallow.person import PersonSchemaV1, ContributorSchemaV1
from oarepo_deposit.models import AccessRight

# TODO: replace with translation function
_ = lambda x: x


class DepositMetadataSchemaV1(Schema, StrictKeysMixin, RefResolverMixin):
    """Common metadata schema."""

    doi = DOIField(missing='')
    publication_date = DateString(required=True)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    creators = fields.Nested(
        PersonSchemaV1, many=True, validate=validate.Length(min=1))
    dates = fields.List(
        fields.Nested(DateSchemaV1), validate=validate.Length(min=1))
    description = MultilingualStringSchemaV1(
        required=True, validate=validate.Length(min=3))
    keywords = fields.List(SanitizedUnicode())
    locations = fields.List(
        fields.Nested(LocationSchemaV1))
    notes = SanitizedHTML()
    version = SanitizedUnicode()
    language = SanitizedUnicode()
    access_right = fields.Str(validate=validate.OneOf(
        choices=[
            AccessRight.OPEN,
            AccessRight.EMBARGOED,
            AccessRight.RESTRICTED,
            AccessRight.CLOSED,
        ],
    ))
    embargo_date = DateString()
    access_conditions = SanitizedHTML()
    subjects = fields.List(SanitizedUnicode())
    contributors = fields.List(fields.Nested(ContributorSchemaV1))
    references = fields.List(SanitizedUnicode(attribute='raw_reference'))
    related_identifiers = fields.Nested(
        RelatedIdentifierSchemaV1, many=True)
    alternate_identifiers = fields.Nested(
        AlternateIdentifierSchemaV1, many=True)
    method = SanitizedUnicode()

    @validates('locations')
    def validate_locations(self, value):
        """Validate that there should be both latitude and longitude."""
        for location in value:
            if (location.get('lon') and not location.get('lat')) or \
                (location.get('lat') and not location.get('lon')):
                raise ValidationError(
                    _('There should be both latitude and longitude.'),
                    field_names=['locations'])

    @validates('language')
    def validate_language(self, value):
        """Validate that language is ISO 639-3 value."""
        if not pycountry.languages.get(alpha_3=value):
            raise ValidationError(
                _('Language must be a lower-cased 3-letter ISO 639-3 string.'),
                field_name='language'
            )

    @validates('dates')
    def validate_dates(self, value):
        """Validate that start date is before the corresponding end date."""
        for interval in value:
            start = arrow.get(interval.get('start'), 'YYYY-MM-DD').date() \
                if interval.get('start') else None
            end = arrow.get(interval.get('end'), 'YYYY-MM-DD').date() \
                if interval.get('end') else None

            if not start and not end:
                raise ValidationError(
                    _('There must be at least one date.'),
                    field_names=['dates']
                )
            if start and end and start > end:
                raise ValidationError(
                    _('"start" date must be before "end" date.'),
                    field_names=['dates']
                )

    @validates('embargo_date')
    def validate_embargo_date(self, value):
        """Validate that embargo date is in the future."""
        if arrow.get(value).date() <= arrow.utcnow().date():
            raise ValidationError(
                _('Embargo date must be in the future.'),
                field_names=['embargo_date']
            )

    @validates('license')
    def validate_license_ref(self, value):
        """Validate if license resolves."""
        if not self.validate_jsonref(value):
            raise ValidationError(
                _('Invalid choice.'),
                field_names=['license'],
            )

    @validates('grants')
    def validate_grants_ref(self, values):
        """Validate if license resolves."""
        for v in values:
            if not self.validate_jsonref(v):
                raise ValidationError(
                    _('Invalid grant.'),
                    field_names=['grants'],
                )

    @validates('doi')
    def validate_doi(self, value):
        """Validate if doi exists."""
        if value and has_request_context():
            required_doi = self.context.get('required_doi')
            if value == required_doi:
                return

            err = ValidationError(_('DOI already exists in Zenodo.'),
                                  field_names=['doi'])

            try:
                doi_pid = PersistentIdentifier.get('doi', value)
            except PIDDoesNotExistError:
                return

            # If the DOI exists, check if it's been assigned to this record
            # by fetching the recid and comparing both PIDs record UUID
            try:
                # If the deposit has not been created yet, raise
                if not self.context.get('recid'):
                    raise err
                recid_pid = PersistentIdentifier.get(
                    'recid', self.context['recid'])
            except PIDDoesNotExistError:
                # There's no way to verify if this DOI belongs to this record
                raise err

            doi_uuid = doi_pid.get_assigned_object()
            recid_uuid = recid_pid.get_assigned_object()

            if doi_uuid and doi_uuid == recid_uuid:
                return
            else:  # DOI exists and belongs to a different record
                raise err

    @validates_schema()
    def validate_license(self, data):
        """Validate license."""
        acc = data.get('access_right')
        if acc in [AccessRight.OPEN, AccessRight.EMBARGOED] and \
            'license' not in data:
            raise ValidationError(
                _('Required when access right is open or embargoed.'),
                field_names=['license']
            )
        if acc == AccessRight.EMBARGOED and 'embargo_date' not in data:
            raise ValidationError(
                _('Required when access right is embargoed.'),
                field_names=['embargo_date']
            )
        if acc == AccessRight.RESTRICTED and 'access_conditions' not in data:
            raise ValidationError(
                _('Required when access right is restricted.'),
                field_names=['access_conditions']
            )

    # TODO: implement custom metadata loader
    # custom = fields.Method('dump_custom', 'load_custom')

    @pre_load()
    def preload_accessrights(self, data):
        """Remove invalid access rights combinations."""
        # Default value
        if 'access_right' not in data:
            data['access_right'] = AccessRight.OPEN

        # Pop values which should not be set for a given access right.
        if data.get('access_right') not in [
            AccessRight.OPEN, AccessRight.EMBARGOED]:
            data.pop('license', None)
        if data.get('access_right') != AccessRight.RESTRICTED:
            data.pop('access_conditions', None)
        if data.get('access_right') != AccessRight.EMBARGOED:
            data.pop('embargo_date', None)

    @pre_load()
    def preload_publicationdate(self, data):
        """Default publication date."""
        if 'publication_date' not in data:
            data['publication_date'] = arrow.utcnow().date().isoformat()

    @post_load()
    def postload_keywords_filter(self, data):
        """Filter empty keywords."""
        if 'keywords' in data:
            data['keywords'] = [
                kw for kw in data['keywords'] if kw.strip()
            ]

    @post_load()
    def postload_references(self, data):
        """Filter empty references and wrap them."""
        if 'references' in data:
            data['references'] = [
                {'raw_reference': ref}
                for ref in data['references'] if ref.strip()
            ]


class DepositRecordSchemaV1(Schema, StrictKeysMixin):
    """Deposit record schema."""

    id = fields.Integer(attribute='pid.pid_value', dump_only=True)
    conceptrecid = SanitizedUnicode(
        attribute='metadata.conceptrecid', dump_only=True)
    doi = SanitizedUnicode(attribute='metadata.doi', dump_only=True)
    conceptdoi = SanitizedUnicode(
        attribute='metadata.conceptdoi', dump_only=True)

    links = fields.Method('dump_links', dump_only=True)
    created = fields.Str(dump_only=True)

    @pre_dump()
    def predump_relations(self, obj):
        """Add relations to the schema context."""
        m = obj.get('metadata', {})
        if 'relations' not in m:
            pid = self.context['pid']
            # For deposits serialize the record's relations
            if is_deposit(m):
                pid = PersistentIdentifier.get('recid', m['recid'])
            m['relations'] = serialize_relations(pid)

        # Remove some non-public fields
        if is_record(m):
            version_info = m['relations'].get('version', [])
            if version_info:
                version_info[0].pop('draft_child_deposit', None)

    def dump_links(self, obj):
        """Dump links."""
        links = obj.get('links', {})
        if current_app:
            links.update(self._dump_common_links(obj))

        try:
            m = obj.get('metadata', {})
            if is_deposit(m):
                links.update(self._dump_deposit_links(obj))
            else:
                links.update(self._dump_record_links(obj))
        except BuildError:
            pass
        return links

    def _thumbnail_url(self, fileobj, thumbnail_size):
        """Create the thumbnail URL for an image."""
        return link_for(
            current_app.config.get('THEME_SITEURL'),
            'thumbnail',
            path=ui_iiif_image_url(
                fileobj,
                size='{},'.format(thumbnail_size),
                image_format='png' if fileobj['type'] == 'png' else 'jpg',
            )
        )

    def _thumbnail_urls(self, recid):
        """Create the thumbnail URL for an image."""
        thumbnail_urls = {}
        cached_sizes = current_app.config.get('CACHED_THUMBNAILS')
        for size in cached_sizes:
            thumbnail_urls[size] = link_for(
                current_app.config.get('THEME_SITEURL'),
                'thumbs',
                id=recid,
                size=size
            )
        return thumbnail_urls

    def _dump_common_links(self, obj):
        """Dump common links for deposits and records."""
        links = {}
        m = obj.get('metadata', {})

        doi = m.get('doi')
        if doi:
            links['badge'] = ui_link_for('badge', doi=quote(doi))
            links['doi'] = idutils.to_url(doi, 'doi', 'https')

        conceptdoi = m.get('conceptdoi')
        if conceptdoi:
            links['conceptbadge'] = ui_link_for('badge', doi=quote(conceptdoi))
            links['conceptdoi'] = idutils.to_url(conceptdoi, 'doi', 'https')

        files = m.get('_files', [])
        for f in files:
            if f.get('type') in thumbnail_exts:
                try:
                    # First previewable image is used for preview.
                    links['thumbs'] = self._thumbnail_urls(m.get('recid'))
                    links['thumb250'] = self._thumbnail_url(f, 250)
                except RuntimeError:
                    pass
                break

        return links

    def _dump_record_links(self, obj):
        """Dump record-only links."""
        links = {}
        m = obj.get('metadata')
        bucket_id = m.get('_buckets', {}).get('record')
        recid = m.get('recid')

        if bucket_id:
            links['bucket'] = api_link_for('bucket', bucket=bucket_id)

        links['html'] = ui_link_for('record_html', id=recid)

        # Generate relation links
        links.update(self._dump_relation_links(m))
        return links

    def _dump_deposit_links(self, obj):
        """Dump deposit-only links."""
        links = {}
        m = obj.get('metadata')
        bucket_id = m.get('_buckets', {}).get('deposit')
        recid = m.get('recid')
        is_published = 'pid' in m.get('_deposit', {})

        if bucket_id:
            links['bucket'] = api_link_for('bucket', bucket=bucket_id)

        # Record links
        if is_published:
            links['record'] = api_link_for('record', id=recid)
            links['record_html'] = ui_link_for('record_html', id=recid)

        # Generate relation links
        links.update(self._dump_relation_links(m))
        return links

    def _dump_relation_links(self, metadata):
        """Dump PID relation links."""
        links = {}
        relations = metadata.get('relations')
        if relations:
            version_info = next(iter(relations.get('version', [])), None)
            if version_info:
                last_child = version_info.get('last_child')
                if last_child:
                    links['latest'] = api_link_for(
                        'record', id=last_child['pid_value'])
                    links['latest_html'] = ui_link_for(
                        'record_html', id=last_child['pid_value'])

                if is_deposit(metadata):
                    draft_child_depid = version_info.get('draft_child_deposit')
                    if draft_child_depid:
                        links['latest_draft'] = api_link_for(
                            'deposit', id=draft_child_depid['pid_value'])
                        links['latest_draft_html'] = ui_link_for(
                            'deposit_html', id=draft_child_depid['pid_value'])
        return links

    @post_load(pass_many=False)
    def remove_envelope(self, data):
        """Post process data."""
        # Remove envelope
        if 'metadata' in data:
            data = data['metadata']

        # Record schema.
        data['$schema'] = \
            'https://oarepo.org/schemas/deposits/records/record-v1.0.0.json'

        return data
