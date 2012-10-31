#
# Copyright (C) 2011, 2012 Satoru SATOH <ssato at redhat.com>
#
import jinja2_cui.render as R
import unittest


class Test_00_functions(unittest.TestCase):

    def test_00_get_fileext(self):
        self.assertEquals(R.get_fileext("a.json"), "json")
        self.assertEquals(R.get_fileext("ajson"), "")

    def test_10_find_loader(self):
        pass

    def test_20_load_context(self):
        pass

    def test_30_load_contexts(self):
        pass

    def test_40_mk_template_paths(self):
        pass

    def test_50_tmpl_env(self):
        pass

    def test_60_render_s(self):
        pass

    def test_70_render_impl(self):
        pass

    def test_80_render(self):
        pass

    def test_90_template_path(self):
        pass

    def test_100_get_ast(self):
        pass

    def test_110_parse_filespec(self):
        pass

    def test_120_parse_and_load_contexts(self):
        pass

    def test_130_parse_template_paths(self):
        pass


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:
