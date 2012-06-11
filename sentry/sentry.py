# -*- coding: utf-8 -*-
from osv import osv
from tools import config
from tools.translate import _
import pooler

from raven import Client


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
    import netsvc
    logger = netsvc.Logger()
    logger.notifyChannel('sentry', netsvc.LOG_INFO,
                         u'Monkeypatching OpenERPDispatcherException!')
    netsvc.OpenERPDispatcherException = SentyDispatcherException


class SentrySetup(osv.osv):
    """Monkeypatch OpenERP logger.
    """
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
        monkeypatch()
        super(SentrySetup, self).__init__(pool, cursor)

SentrySetup()
