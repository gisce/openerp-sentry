# -*- coding: utf-8 -*-
# This file is part of openerp-sentry. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
from itsbroken.testing import drop_database

from .test_main import TestMain


def tearDownModule():
    """
    Drop the database at the end of this test module
    Works only with unittest2 (default in python 2.7+)
    """
    drop_database()


def suite():
    _suite = unittest.TestSuite()
    _suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestMain),
    ])
    return _suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())