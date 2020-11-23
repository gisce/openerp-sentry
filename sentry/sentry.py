# -*- coding: utf-8 -*-
# This file is part of openerp-sentry. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import os
from osv import osv
import pooler
from tools import config
import release
import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.rq import RqIntegration
import subprocess
import logging
from signals import NETSVC_DISPATCH_EXCEPTION


logger = logging.getLogger('openerp.sentry')


class ExecuteInDir(object):
    def __init__(self, d):
        self.cd = os.getcwd()
        self.d = d

    def __enter__(self):
        os.chdir(self.d)

    def __exit__(self, *a, **kw):
        os.chdir(self.cd)


def get_release():
    with ExecuteInDir(os.path.join(config['root_path'])):
        git = subprocess.check_output(['git', 'describe', '--tags']).strip()
    return '{}@{}-{}'.format(
        release.name,
        release.version,
        git
    )


class Client(object):

    @staticmethod
    def captureException():
        sentry_sdk.capture_exception()

    @staticmethod
    def captureMessage(message, level=None, scope=None, **scope_args):
        sentry_sdk.capture_message(message, level, scope, scope_args)


def send_to_sentry(dispatcher, service_name, method, params, exception):
    # Ugly hack to know wich type of exception it is.
    # From client code: bin/rpc.py L:46
    exc_type = unicode(exception).split(' -- ')[0]
    # Predefined excptions from client code: bin/rpc.py L:177
    if exc_type not in ('warning', 'UserError'):
        with sentry_sdk.configure_scope() as scope:
            db, pool = pooler.get_db_and_pool(config['db_name'])
            cursor = db.cursor()
            user = pool.get('res.users').browse(cursor, 1, params[1])
            scope.user = {
                'id': params[1],
                'username': user.login,
                'name': user.name,
                'email': user.address_id and user.address_id.email or None,
                'ip_address': dispatcher.client_ip
            }
            cursor.close()
            scope.set_tag('service_name', service_name),
            scope.set_tag('method', method)
            sentry_sdk.capture_exception(exception)


NETSVC_DISPATCH_EXCEPTION.connect(send_to_sentry)


def begore_send(event, hint):
    if event.get('logger', '').startswith('openerp'):
        return None
    return event


class SentrySetup(osv.osv):
    """Monkeypatch OpenERP logger.
    """
    _name = 'sentry.setup'

    def __init__(self, pool, cursor):
        dsn_env = os.getenv('SENTRY_DSN')
        dsn = config.get('sentry_dsn')
        app_release = get_release()
        environment = config.get('environment', 'staging')
        traces_sample_rate = float(config.get('sentry_traces_sample_rate', 0))
        if dsn_env:
            config['sentry_dsn'] = dsn_env
            logger.info('Updating sentry_dsn=%s conf from environment var', dsn_env)
        elif dsn:
            os.environ['SENTRY_DSN'] = dsn
            logger.info('Setting up SENTRY_DSN=%s environment var', dsn)
        logger.info(
            'Sentry setup: release: %s, environment: %s, sample_rate: %s',
            app_release, environment, traces_sample_rate
        )
        sentry_sdk.init(
            release=app_release,
            environment=environment,
            traces_sample_rate=traces_sample_rate,
            before_send=begore_send,
            integrations=[RedisIntegration(), FlaskIntegration(), RqIntegration()]
        )
        self.client = Client()
        super(SentrySetup, self).__init__(pool, cursor)

    def test(self, cursor, uid, context=None):
        if context is None:
            context = {}
        raise Exception('This is a sentry test exception')

    def test_logger(self, cursor, uid, message, logger='openerp.sentry'):
        test_logger = logging.getLogger(logger)
        test_logger.error(message)


SentrySetup()
