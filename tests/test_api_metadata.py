# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test validation in OArepo deposit REST API."""
import json

import pytest


def test_minimal_create(db, api_client, es, json_headers,
                        deposit_url, get_json, minimal_record):
    """Test minimal deposit record creation."""
    client = api_client
    headers = json_headers

    res = client.post(deposit_url,
                      data=json.dumps(dict(metadata=minimal_record)),
                      headers=headers)
    body = get_json(res)
    assert res.status_code == 201, body
    assert 0 == res.get('hits').get('total')


def test_invalid_create(db, api_client, es, json_headers, deposit_url,
                        get_json):
    """Test invalid deposit creation."""
    client = api_client
    headers = json_headers

    # Invalid deposits.
    cases = [
        {
            '$schema': 'https://oarepo.org/schemas/deposit-v1.0.0.json',
            'unknownkey': 'data',
            'metadata': {}
        },
        dict(metadata={}),
    ]

    for case in cases:
        res = client.post(deposit_url, data=json.dumps(case), headers=headers)
        assert res.status_code == 400, case

    # No deposits were created
    res = get_json(client.get(deposit_url, headers=headers), code=200)
    assert 0 == res.get('hits').get('total')


def test_invalid_schema(db, api_client, es, json_headers, deposit_url, get_json):
    client = api_client
    headers = json_headers

    # Invalid deposits.
    cases = [
        {
            '$schema': 'https://oarepo.org/schemas/nope-v1.0.0.json',
            'metadata': {}
        },
        {
            '$schema': 'https://nope.org/schemas/deposit-v1.0.0.json',
            'metadata': {}
        }
    ]
    for case in cases:
        with pytest.raises(AttributeError):
            print(case)
            client.post(deposit_url, data=json.dumps(case), headers=headers)

    # No deposits were created
    res = get_json(client.get(deposit_url, headers=headers), code=200)
    assert 0 == res.get('hits').get('total')
