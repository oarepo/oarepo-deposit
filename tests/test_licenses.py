# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test license handling."""
from click.testing import CliRunner
from invenio_opendefinition.cli import loadlicenses


def test_load_licenses(db, api_client, es, json_headers, licenses_url, get_json):
    client = api_client
    headers = json_headers

    out = CliRunner().invoke(loadlicenses, ['eager'])
    print(out)

    # No deposits were created
    res = get_json(client.get(licenses_url, headers=headers), code=200)
    assert 100 == res.get('hits').get('total')
