# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Base Deposit record loaders."""
from __future__ import absolute_import, print_function

from flask import has_request_context, request

from oarepo_deposit.marshmallow.errors import MarshmallowErrors


def json_loader(pre_validator=None, post_validator=None, translator=None):
    """Basic JSON loader with translation and pre/post validation support."""

    def loader(data=None):
        data = data or request.json

        if pre_validator:
            pre_validator(data)
        if translator:
            data = translator(data)
        if post_validator:
            post_validator(data)

        return data

    return loader


def marshmallow_loader(schema_class, **kwargs):
    """Basic marshmallow loader generator."""

    def translator(data):
        # Replace refs when we are in request context.
        context = dict(replace_refs=has_request_context())

        # DOI validation context
        if request and request.view_args.get('pid_value'):
            _, record = request.view_args.get('pid_value').data
            context['recid'] = record['recid']

        # Extra context
        context.update(kwargs)

        # Load data
        result = schema_class(context=context).load(data)
        if result.errors:
            raise MarshmallowErrors(result.errors)
        return result.data

    return translator
