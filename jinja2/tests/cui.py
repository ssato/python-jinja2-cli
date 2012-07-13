#
# Copyright (C) 2011, 2012 Satoru SATOH <satoru.satoh @ gmail.com>
#
import jinja2.cui as C
import unittest


class Test_functions(unittest.TestCase):

    def test_is_dict(self):
        self.assertTrue(C.is_dict({}))
        self.assertTrue(C.is_dict({"a": 1}))
        self.assertFalse(C.is_dict([]))
        self.assertFalse(C.is_dict(None))

    def test_is_iterable(self):
        self.assertTrue(C.is_iterable([1, 2]))
        self.assertTrue(C.is_iterable((1, 2)))
        self.assertTrue(C.is_iterable((x for x in range(10))))
        self.assertFalse(C.is_iterable({}))
        self.assertFalse(C.is_iterable(None))


class TestMyDict(unittest.TestCase):

    def test_createFromDict(self):
        self.assertTrue(isinstance(C.MyDict.createFromDict({}), C.MyDict))

        md = C.MyDict.createFromDict({"a": {"b": 1}, "c": 2, "d": [3, 4]})
        self.assertTrue(isinstance(md, C.MyDict))
        self.assertTrue(isinstance(md["a"], C.MyDict))

    def test_update(self):
        md1 = C.MyDict.createFromDict({"a": {"b": 1}, "c": 2})
        md2 = C.MyDict.createFromDict({"a": {"b": 2, "d": 3}, "e": 4})

        md1.update(md2)

        self.assertEquals(md1["a"]["b"], md2["a"]["b"])
        self.assertEquals(md1["a"]["d"], md2["a"]["d"])
        self.assertEquals(md1["c"], 2)
        self.assertEquals(md1["e"], md2["e"])

    def test_update__w_merge_lists(self):
        md1 = C.MyDict.createFromDict({"a": [1, 2]})
        md2 = C.MyDict.createFromDict({"a": [3, 4]})

        md1.update(md2, merge_lists=True)

        self.assertEquals(md1["a"], [1, 2, 3, 4])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_functions))
    suite.addTest(unittest.makeSuite(TestMyDict))
    return suite


# vim:sw=4:ts=4:et:
