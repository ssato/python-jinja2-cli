#
# Copyright (C) 2011 - 2013 Satoru SATOH <ssato at redhat.com>
#
import os
import unittest

import jinja2_cli.render as TT  # Stands for Test Target module.
import jinja2_cli.tests.common as C


class Test_00_pure_functions(unittest.TestCase):

    def test_00_mk_template_paths__wo_paths(self):
        self.assertEquals(TT.mk_template_paths("/a/b/c.yml"),
                          [os.curdir, "/a/b"])

    def test_01_mk_template_paths__w_paths(self):
        self.assertEquals(TT.mk_template_paths("/a/b/c.yml", ["/a/d"]),
                          ["/a/d", "/a/b"])

    def test_10_tmpl_env(self):
        self.assertTrue(isinstance(TT.tmpl_env(["/a/b", ]),
                                   TT.jinja2.Environment))

    def test_20_render_s(self):
        tmpl_s = 'a = {{ a }}, b = "{{ b }}"'
        self.assertEquals(TT.render_s(tmpl_s, {'a': 1, 'b': 'bbb'}),
                          'a = 1, b = "bbb"')

    def test_30_parse_template_paths__wo_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml"),
                          [os.curdir, "/a/b"])

    def test_31_parse_template_paths__w_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml", "/a/d:/a/e"),
                          ["/a/d", "/a/e", "/a/b"])


class Test_10_effectful_functions(unittest.TestCase):

    def setUp(self):
        self.workdir = C.setup_workdir()

    def test_10_render_impl(self):
        tmpl = "a.j2"
        open(os.path.join(self.workdir, tmpl), 'w').write("a = {{ a }}")

        r = TT.render_impl(tmpl, {'a': "aaa", }, [self.workdir])
        self.assertEquals(r, "a = aaa")

    def test_20_render(self):
        tmpl = "a.j2"
        open(os.path.join(self.workdir, tmpl), 'w').write("a = {{ a }}")

        r = TT.render(tmpl, {'a': "aaa", }, [self.workdir])
        self.assertEquals(r, "a = aaa")

    def test_22_render__ask(self):
        """FIXME: Write tests for jinja2_cli.render.render"""
        pass

    def test_30_template_path(self):
        tmpl = "a.j2"
        open(os.path.join(self.workdir, tmpl), 'w').write("a = {{ a }}")

        self.assertEquals(TT.template_path(tmpl, [self.workdir]),
                          os.path.join(self.workdir, tmpl))

    def test_32_template_path__not_exist(self):
        tmpl = "template_not_exist.j2"

        self.assertTrue(TT.template_path(tmpl, [self.workdir]) is None)

    def test_50_renderto(self):
        tmpl = "a.j2"
        output = os.path.join(self.workdir, "a.out")
        open(os.path.join(self.workdir, tmpl), 'w').write("a = {{ a }}")

        TT.renderto(tmpl, dict(a="aaa", ), [self.workdir], output, False)
        self.assertEquals(TT.compat.copen(output).read(), "a = aaa")

# vim:sw=4:ts=4:et:
