#
# U.pyright (U. 2011, 2012 Satoru SATOH <ssato at redhat.com>
#
import jinja2_cui.utils as U
import unittest


class Test_00_functions(unittest.TestCase):

    def test_00_is_dict(self):
        self.assertTrue(U.is_dict({}))
        self.assertTrue(U.is_dict({"a": 1}))
        self.assertFalse(U.is_dict([]))
        self.assertFalse(U.is_dict(None))

    def test_01_is_iterable(self):
        self.assertTrue(U.is_iterable([1, 2]))
        self.assertTrue(U.is_iterable((1, 2)))
        self.assertTrue(U.is_iterable((x for x in range(10))))
        self.assertFalse(U.is_iterable({}))
        self.assertFalse(U.is_iterable(None))

    def test_02_uniq(self):
        self.assertEquals(U.uniq([]), [])
        self.assertEquals(
            U.uniq([1, 4, 5, 1, 2, 3, 5, 10, 13, 2]),
            [1, 4, 5, 2, 3, 10, 13]
        )

    def test_03_chaincalls(self):
        self.assertEquals(
            U.chaincalls([lambda x: x + 1, lambda x: x - 1], 1),
            1
        )

    def test_04_normpath(self):
        self.assertEquals(U.normpath("/tmp/../etc/hosts"), "/etc/hosts")
        self.assertEquals(U.normpath("~root/t"), "/root/t")

    def test_05_flip(self):
        self.assertEquals(U.flip((1, 3)), (3, 1))

    def test_06_concat(self):
        self.assertEquals(U.concat([]), [])
        self.assertEquals(U.concat(()), [])
        self.assertEquals(U.concat([[1, 2, 3], [4, 5]]), [1, 2, 3, 4, 5])
        self.assertEquals(
            U.concat([[1, 2, 3], [4, 5, [6, 7]]]), [1, 2, 3, 4, 5, [6, 7]]
        )
        self.assertEquals(
            U.concat(((1, 2, 3), (4, 5, [6, 7]))), [1, 2, 3, 4, 5, [6, 7]]
        )
        self.assertEquals(
            U.concat((i, i * 2) for i in range(3)), [0, 0, 1, 2, 2, 4]
        )


class TestMyDict(unittest.TestCase):

    def test_createFromDict(self):
        self.assertTrue(isinstance(U.MyDict.createFromDict({}), U.MyDict))

        md = U.MyDict.createFromDict({"a": {"b": 1}, "c": 2, "d": [3, 4]})
        self.assertTrue(isinstance(md, U.MyDict))
        self.assertTrue(isinstance(md["a"], U.MyDict))

    def test_update(self):
        md1 = U.MyDict.createFromDict({"a": {"b": 1}, "c": 2})
        md2 = U.MyDict.createFromDict({"a": {"b": 2, "d": 3}, "e": 4})

        md1.update(md2)

        self.assertEquals(md1["a"]["b"], md2["a"]["b"])
        self.assertEquals(md1["a"]["d"], md2["a"]["d"])
        self.assertEquals(md1["c"], 2)
        self.assertEquals(md1["e"], md2["e"])

    def test_update__w_merge_lists(self):
        md1 = U.MyDict.createFromDict({"a": [1, 2]})
        md2 = U.MyDict.createFromDict({"a": [3, 4]})

        md1.update(md2, merge_lists=True)

        self.assertEquals(md1["a"], [1, 2, 3, 4])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_functions))
    suite.addTest(unittest.makeSuite(TestMyDict))
    return suite


# vim:sw=4:ts=4:et:
