# -*- coding: utf-8 -*-

import logging

from .scrobbler import ScrobServer

__alias__ = 'Last.fm'
__feeluown_version__ = '3.10.0'
__version__ = '0.0.1'
__desc__ = 'Last.fm'

logger = logging.getLogger(__name__)


def enable(app):
    scrobbler = ScrobServer(app)


def disable(app):
    pass
