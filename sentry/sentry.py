# -*- coding: utf-8 -*-
# This file is part of openerp-sentry. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import os
from osv import osv
from tools import config
import pooler
import netsvc

from raven import Client


def log(msg, level=netsvc.LOG_INFO):
    logger = netsvc.Logger()
    logger.notifyChannel('sentry', netsvc.LOG_INFO, msg)


class SentyDispatcherException(Exception):
    def __init__(self, exception, traceback):
        # Ugly hack to know wich type of exception it is.
        # From client code: bin/rpc.py L:46
        exc_type = unicode(exception).split(' -- ')[0]
        # Predefined excptions from client code: bin/rpc.py L:177
        if exc_type not in ('warning', 'UserError'):
            if config.get('db_name', False):
                sentry = pooler.get_pool(config['db_name']).get('sentry.setup')
                if sentry:
                    sentry.client.captureException()
        self.exception = exception
        self.traceback = traceback


def monkeypatch():
    log(u'Monkeypatching OpenERPDispatcherException!')
    netsvc.OpenERPDispatcherException = SentyDispatcherException


class SentrySetup(osv.osv):
    """Monkeypatch OpenERP logger.
    """
    _name = 'sentry.setup'

    def __init__(self, pool, cursor):
        processors = (
            'raven.processors.SanitizePasswordsProcessor',
            'raven_sanitize_openerp.OpenerpPasswordsProcessor'
        )
        dsn_env = os.getenv('SENTRY_DSN')
        dsn = config.get('sentry_dsn')
        if dsn_env:
            config['sentry_dsn'] = dsn_env
            log('Updating sentry_dsn=%s conf from environment var' % dsn_env)
        elif dsn:
            os.environ['SENTRY_DSN'] = dsn
            log('Setting up SENTRY_DSN=%s environment var' % dsn)
        self.client = Client(processors=processors)
        monkeypatch()
        super(SentrySetup, self).__init__(pool, cursor)

SentrySetup()
