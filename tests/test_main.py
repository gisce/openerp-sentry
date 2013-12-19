# -*- coding: utf-8 -*-
# This file is part of openerp-sentry. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest

from itsbroken.transaction import Transaction
from itsbroken.testing import DB_NAME, POOL, USER, CONTEXT, install_module, drop_database

class TestMain(unittest.TestCase):
    """
    Tests
    """

    def setUp(self):
        install_module('product')


    def test_0010_create(self):
        """
        Test by creating a new partner
        """
        with Transaction().start(DB_NAME, USER, CONTEXT) as txn:
            partner_obj = POOL.get('res.partner')

            values = {
                'name': 'Sharoon Thomas'
            }
            id = partner_obj.create(
                txn.cursor, txn.user, values, txn.context
            )
            partner = partner_obj.browse(txn.cursor, txn.user, id)
            self.assertEqual(partner.name, values['name'])

    def test_0020_one(self):
        """
        Tests
        """
        self.assertEqual(1 + 1, 2)



def suite():
    """
Test suite
"""
    _suite = unittest.TestSuite()
    _suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestMain),
    ])
    return _suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())