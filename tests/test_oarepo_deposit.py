# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from oarepo_deposit import OARepoDeposit


def test_version():
    """Test version import."""
    from oarepo_deposit import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = OARepoDeposit(app)
    assert 'oarepo-deposit' in app.extensions

    app = Flask('testapp')
    ext = OARepoDeposit()
    assert 'oarepo-deposit' not in app.extensions
    ext.init_app(app)
    assert 'oarepo-deposit' in app.extensions
