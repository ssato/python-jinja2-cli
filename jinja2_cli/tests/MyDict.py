#
# Copyright (C). 2011 - 2013 Satoru SATOH <ssato at redhat.com>
#
import jinja2_cli.MyDict as TT
import unittest


class Test_00_functions(unittest.TestCase):

    def test_00_is_dict(self):
        self.assertTrue(TT.is_dict({}))
        self.assertTrue(TT.is_dict({"a": 1}))
        self.assertFalse(TT.is_dict([]))
        self.assertFalse(TT.is_dict(None))

    def test_01_is_iterable(self):
        self.assertTrue(TT.is_iterable([1, 2]))
        self.assertTrue(TT.is_iterable((1, 2)))
        self.assertTrue(TT.is_iterable((x for x in range(10))))
        self.assertFalse(TT.is_iterable({}))
        self.assertFalse(TT.is_iterable(None))


class Test_10_MyDict(unittest.TestCase):

    def test_createFromDict(self):
        self.assertTrue(isinstance(TT.MyDict.createFromDict({}), TT.MyDict))

        md = TT.MyDict.createFromDict({"a": {"b": 1}, "c": 2, "d": [3, 4]})
        self.assertTrue(isinstance(md, TT.MyDict))
        self.assertTrue(isinstance(md["a"], TT.MyDict))

    def test_update(self):
        md1 = TT.MyDict.createFromDict({"a": {"b": 1}, "c": 2})
        md2 = TT.MyDict.createFromDict({"a": {"b": 2, "d": 3}, "e": 4})

        md1.update(md2)

        self.assertEquals(md1["a"]["b"], md2["a"]["b"])
        self.assertEquals(md1["a"]["d"], md2["a"]["d"])
        self.assertEquals(md1["c"], 2)
        self.assertEquals(md1["e"], md2["e"])

    def test_update__w_merge_lists(self):
        md1 = TT.MyDict.createFromDict({"a": [1, 2]})
        md2 = TT.MyDict.createFromDict({"a": [3, 4]})

        md1.update(md2, merge_lists=True)

        self.assertEquals(md1["a"], [1, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:
