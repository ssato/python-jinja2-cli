#
# Copyright (C) 2011, 2012 Satoru SATOH <ssato at redhat.com>
#
import jinja2_cui.render as R
import unittest


class Test_functions(unittest.TestCase):

    def test_is_dict(self):
        self.assertTrue(R.is_dict({}))
        self.assertTrue(R.is_dict({"a": 1}))
        self.assertFalse(R.is_dict([]))
        self.assertFalse(R.is_dict(None))

    def test_is_iterable(self):
        self.assertTrue(R.is_iterable([1, 2]))
        self.assertTrue(R.is_iterable((1, 2)))
        self.assertTrue(R.is_iterable((x for x in range(10))))
        self.assertFalse(R.is_iterable({}))
        self.assertFalse(R.is_iterable(None))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_functions))
    return suite


# vim:sw=4:ts=4:et:
