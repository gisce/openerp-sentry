openerp-sentry
==============

.. image:: https://secure.travis-ci.org/alainivars/openerp-sentry.png?branch=master
   :target: http://travis-ci.org/alainivars/openerp-sentry

.. image:: https://coveralls.io/repos/alainivars/openerp-sentry/badge.png
   :target: https://coveralls.io/r/alainivars/openerp-sentry

.. image:: https://d2weczhvl823v0.cloudfront.net/alainivars/openerp-sentry/trend.png
   :target: https://bitdeli.com/free


Sentry logger for OpenERP

Configuration
-------------

1. Generate Sentry DSN
2. Add the keyword `sentry_dsn` in your openerp server config file
3. Install dependencies `pip install -r reqs.txt
4. Install sentry module in the OpenERP
5. Edit the openerp/netsvc.py and add the needs...
6. Enjoy it!


openerp/netsvc.py needs
-----------------------

replace:
--------
    import openerp
    _logger = logging.getLogger(__name__)

by:
---
    import openerp
    from raven import Client
    processors = (
        'raven.processors.SanitizePasswordsProcessor',
        'raven_sanitize_openerp.OpenerpPasswordsProcessor'
    )
    client = Client('http://<your_key>@sentry:<your_port>/<your_group_in_sentry>', processors=processors)
    client.captureMessage('Sentry Tracking Actived!')
    _logger = logging.getLogger(__name__)

and replace:
------------
    except openerp.exceptions.AccessError:
        raise
    except openerp.exceptions.AccessDenied:
        raise
    except openerp.exceptions.Warning:
        raise
    except openerp.exceptions.DeferredException, e:
        _logger.exception(tools.exception_to_unicode(e))
        post_mortem(e.traceback)
        raise
    except Exception, e:
        _logger.exception(tools.exception_to_unicode(e))
        post_mortem(sys.exc_info())
        raise

by:
---
    except openerp.exceptions.AccessError:
	    client.captureException() # openerp-sentry
        raise
    except openerp.exceptions.AccessDenied:
	    client.captureException() # openerp-sentry
        raise
    except openerp.exceptions.Warning:
	    client.captureException() # openerp-sentry
        raise
    except openerp.exceptions.DeferredException, e:
        _logger.exception(tools.exception_to_unicode(e))
	    client.captureException() # openerp-sentry
        post_mortem(e.traceback)
        raise
    except Exception, e:
        _logger.exception(tools.exception_to_unicode(e))
	    client.captureException() # openerp-sentry
        post_mortem(sys.exc_info())
        raise


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



[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/alainivars/openerp-sentry/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

