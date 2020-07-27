# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""" Common data model for OA repository records according to Zenodo deposit model"""

from flask_babelex import gettext as _

from . import config


class OARepoDeposit(object):
    """OARepo-Deposit extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['oarepo-deposit'] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('OAREPO_DEPOSIT_'):
                app.config.setdefault(k, getattr(config, k))
