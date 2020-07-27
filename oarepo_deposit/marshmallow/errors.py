# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
import json

from invenio_rest.errors import RESTValidationError


class MarshmallowErrors(RESTValidationError):
    """Marshmallow validation errors."""

    def __init__(self, errors):
        """Store marshmallow errors."""
        self.errors = errors
        super(MarshmallowErrors, self).__init__()

    def __str__(self):
        """Print exception with errors."""
        return "{base}. Encountered errors: {errors}".format(
            base=super(RESTValidationError, self).__str__(),
            errors=self.errors)

    def iter_errors(self, errors, prefix=''):
        """Iterator over marshmallow errors."""
        res = []
        for field, error in errors.items():
            if isinstance(error, list):
                res.append(dict(
                    field='{0}{1}'.format(prefix, field),
                    message=' '.join([str(x) for x in error])
                ))
            elif isinstance(error, dict):
                res.extend(self.iter_errors(
                    error,
                    prefix='{0}{1}.'.format(prefix, field)
                ))
        return res

    def get_body(self, environ=None):
        """Get the request body."""
        body = dict(
            status=self.code,
            message=self.get_description(environ),
        )

        if self.errors:
            body['errors'] = self.iter_errors(self.errors)

        return json.dumps(body)
