# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""

# TODO: replace with translation function
from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS
from invenio_records_rest.config import RECORDS_REST_ENDPOINTS

_ = lambda x: x

PIDSTORE_RECID_FIELD = 'recid'

RECORDS_REST_ENDPOINTS.update(OPENDEFINITION_REST_ENDPOINTS)

OAREPO_RELATION_TYPES = [
    ('isCitedBy', _('Cited by')),
    ('cites', _('Cites')),
    ('isSupplementTo', _('Supplement to')),
    ('isSupplementedBy', _('Supplementary material')),
    ('references', _('References')),
    ('isReferencedBy', _('Referenced by')),
    ('isNewVersionOf', _('Previous versions')),
    ('isPreviousVersionOf', _('New versions')),
    ('isContinuedBy', _('Continued by')),
    ('continues', _('Continues')),
    ('isPartOf', _('Part of')),
    ('hasPart', _('Has part')),
    ('isReviewedBy', _('Reviewed by')),
    ('reviews', _('Reviews')),
    ('isDocumentedBy', _('Documented by')),
    ('documents', _('Documents')),
    ('compiles', _('Compiles')),
    ('isCompiledBy', _('Compiled by')),
    ('isDerivedFrom', _('Derived from')),
    ('isSourceOf', _('Source of')),
    ('isIdenticalTo', _('Identical to')),
]

#: Allow list of contributor types with DC<>MARC mapping.
OAREPO_DEPOSIT_CONTRIBUTOR_TYPES = [
    dict(label='Contact person', marc='prc', datacite='ContactPerson'),
    dict(label='Data collector', marc='col', datacite='DataCollector'),
    dict(label='Data curator', marc='cur', datacite='DataCurator'),
    dict(label='Data manager', marc='dtm', datacite='DataManager'),
    dict(label='Distributor', marc='dst', datacite='Distributor'),
    dict(label='Editor', marc='edt', datacite='Editor'),
    dict(label='Hosting institution', marc='his',
         datacite='HostingInstitution'),
    dict(label='Other', marc='oth', datacite='Other'),
    dict(label='Producer', marc='pro', datacite='Producer'),
    dict(label='Project leader', marc='pdr', datacite='ProjectLeader'),
    dict(label='Project manager', marc='rth', datacite='ProjectManager'),
    dict(label='Project member', marc='rtm', datacite='ProjectMember'),
    dict(label='Registration agency', marc='cor',
         datacite='RegistrationAgency'),
    dict(label='Registration authority', marc='cor',
         datacite='RegistrationAuthority'),
    dict(label='Related person', marc='oth', datacite='RelatedPerson'),
    dict(label='Research group', marc='rtm', datacite='ResearchGroup'),
    dict(label='Researcher', marc='res', datacite='Researcher'),
    dict(label='Rights holder', marc='cph', datacite='RightsHolder'),
    dict(label='Sponsor', marc='spn', datacite='Sponsor'),
    dict(label='Supervisor', marc='dgs', datacite='Supervisor'),
    dict(label='Work package leader', marc='led',
         datacite='WorkPackageLeader'),
]
OAREPO_DEPOSIT_CONTRIBUTOR_MARC2DATACITE = {
    x['marc']: x['datacite'] for x in OAREPO_DEPOSIT_CONTRIBUTOR_TYPES
}
OAREPO_DEPOSIT_CONTRIBUTOR_DATACITE2MARC = {
    x['datacite']: x['marc'] for x in OAREPO_DEPOSIT_CONTRIBUTOR_TYPES
}
OAREPO_DEPOSIT_CONTRIBUTOR_TYPES_LABELS = {
    x['datacite']: x['label'] for x in OAREPO_DEPOSIT_CONTRIBUTOR_TYPES
}
