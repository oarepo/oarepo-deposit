# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo-Deposit is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""" Common data model for OA repository records according to Zenodo deposit model"""

from .ext import OARepoDeposit
from .version import __version__

__all__ = ('__version__', 'OARepoDeposit')
