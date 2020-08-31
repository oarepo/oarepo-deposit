# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test validation in OArepo deposit REST API."""
import json


def test_invalid_create(db, api_client, es, json_headers, deposit_url,
                        get_json):
    """Test invalid deposit creation."""
    client = api_client
    headers = json_headers

    # Invalid deposits.
    cases = [
        dict(unknownkey='data', metadata={}),
        dict(metadat={}),
    ]

    for case in cases:
        res = client.post(deposit_url, data=json.dumps(case), headers=headers)
        assert res.status_code == 400, case

    # No deposits were created
    assert 0 == len(
        get_json(client.get(deposit_url, headers=headers), code=200))
