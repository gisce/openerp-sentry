openerp-sentry
==============

Sentry logger for OpenERP

Configuration
-------------

1. Generate Sentry DSN
2. Add the keyword `sentry_dsn` in your openerp server config file
3. Install dependencies `pip install -r reqs.txt
4. Install sentry module in the OpenERP
5. Enjoy it!

Usage
-----

* All uncaught exceptions will be processed with Sentry logger.
* `osv.except_osv` exceptions won't be processed`.
* You can use raven client from your OpenERP instance.

```python
def create(self, cursor, uid, vals, context=None)
    client = self.pool.get('sentry.setup').client
    client.captureMessage('Hello world!')
```

You can see all the documentation for raven here: http://raven.readthedocs.org

