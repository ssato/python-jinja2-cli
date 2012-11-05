#
# Copyright (C) 2012 Satoru SATOH <ssato at redhat.com>
#
import jinja2_cui.contexts as C
import unittest


class Test_00_functions(unittest.TestCase):

    def test_00_get_fileext(self):
        self.assertEquals(C.get_fileext("a.json"), "json")
        self.assertEquals(C.get_fileext("ajson"), "")

    def test_10_find_loader(self):
        mockloaders = dict(json=0, yaml=1)
        self.assertEquals(C.find_loader("a.json", loaders=mockloaders),  0)
        self.assertEquals(C.find_loader("a.yaml", loaders=mockloaders),  1)

    def test_20_load_context(self):
        pass

    def test_30_load_contexts(self):
        pass

    def test_40_parse_filespec(self):
        pass

    def test_50_parse_and_load_contexts(self):
        pass


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:
