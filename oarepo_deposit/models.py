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
from invenio_search import RecordsSearch, current_search_client

# TODO: replace with translation function
_ = lambda x: x


class AccessRight(object):
    """Class defining access right status."""

    OPEN = 'open'
    EMBARGOED = 'embargoed'
    RESTRICTED = 'restricted'
    CLOSED = 'closed'

    _all = (
        (OPEN, _('Open Access')),
        (EMBARGOED, _('Embargoed Access')),
        (RESTRICTED, _('Restricted Access')),
        (CLOSED, _('Closed Access')),
    )

    _icon = {
        OPEN: 'fa-unlock',
        EMBARGOED: 'fa-ban',
        RESTRICTED: 'fa-key',
        CLOSED: 'fa-lock',
    }

    _description = {
        OPEN: _('Files are publicly accessible.'),
        EMBARGOED: _('Files are currently under embargo but will be publicly '
                     'accessible after {date}.'),
        RESTRICTED: _('You may request access to the files in this upload, '
                      'provided that you fulfil the conditions below. The '
                      'decision whether to grant/deny access is solely under '
                      'the responsibility of the record owner.'),
        CLOSED: _('Files are not publicly accessible.'),
    }

    _category = {
        OPEN: 'success',
        EMBARGOED: 'warning',
        RESTRICTED: 'danger',
        CLOSED: 'danger',
    }

    @staticmethod
    def is_embargoed(embargo_date):
        """Test if date is still under embargo."""
        return arrow.get(embargo_date).date() > datetime.utcnow().date()

    @classmethod
    def is_valid(cls, value):
        """Test if access right is valid."""
        return bool([key for key, title in cls._all if key == value])

    @classmethod
    def get(cls, value, embargo_date=None):
        """Get access right."""
        if embargo_date is not None and cls.EMBARGOED == value and \
            not cls.is_embargoed(embargo_date):
            return cls.OPEN

        return value

    @classmethod
    def as_icon(cls, value):
        """Get icon for a specific status."""
        return cls._icon[value]

    @classmethod
    def as_title(cls, value):
        """Get title for a specific status."""
        return dict(cls._all)[value]

    @classmethod
    def as_description(cls, value, embargo_date=None):
        """Get description for a specific status."""
        return cls._description[value].format(
            date=format_date(embargo_date, 'long'))

    @classmethod
    def as_category(cls, value, **kwargs):
        """Get title for a specific status."""
        cat = cls._category[value]
        return kwargs[cat] if cat in kwargs else cat

    @classmethod
    def as_options(cls):
        """Return list of access rights as options."""
        return cls._all

    @classmethod
    def get_expired_embargos(cls):
        """Get records for which the embargo period have expired."""
        endpoint = current_app.config['RECORDS_REST_ENDPOINTS']['recid']

        s = RecordsSearch(
            using=current_search_client,
            index=endpoint['search_index']
        ).query(
            'query_string',
            query='access_right:{0} AND embargo_date:{{* TO {1}}}'.format(
                cls.EMBARGOED,
                # Uses timestamp instead of date on purpose.
                datetime.utcnow().isoformat()
            ),
            allow_leading_wildcard=False
        ).source(False)

        return [hit.meta.id for hit in s.scan()]
