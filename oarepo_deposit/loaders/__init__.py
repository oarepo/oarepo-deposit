# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Common data model for OA repository records according to Zenodo deposit model."""
from __future__ import absolute_import, print_function

from .base import json_loader, marshmallow_loader
from ..marshmallow.deposit import DepositRecordSchemaV1

# Translators
# ===========
#: JSON v1 deposit translator.
deposit_json_v1_translator = marshmallow_loader(DepositRecordSchemaV1)

# Loaders
# =======
#: JSON deposit record loader.
deposit_json_v1 = json_loader(
    translator=deposit_json_v1_translator,
)
