# -*- coding: utf-8 -*-
# This file is part of openerp-sentry. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from openerp.osv import osv
from openerp.tools import config
from openerp.tools.translate import _


class SentrySetup(osv.osv):
    """Make sentry capture the logs once OpenERP starts"""
    _name = 'sentry.setup'

    def __init__(self, pool, cursor):
        if not config.get('sentry_dsn', False):
            raise osv.except_osv(
                _(u'Error'),
                _(u'No sentry DSN configured in config file.')
            )
        processors = (
            'raven.processors.SanitizePasswordsProcessor',
            'raven_sanitize_openerp.OpenerpPasswordsProcessor'
        )
        self.client = Client(dsn=config['sentry_dsn'], processors=processors)
        handler = SentryHandler(self.client)
        setup_logging(handler)
        super(SentrySetup, self).__init__(pool, cursor)

SentrySetup()
