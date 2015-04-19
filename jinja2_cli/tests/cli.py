#
# Copyright (C) 2015 Satoru SATOH <ssato at redhat.com>
#
import os
import unittest

import jinja2_cli.cli as TT


class Test_00_pure_functions(unittest.TestCase):

    def test_10_parse_template_paths__wo_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml"),
                          [os.curdir, "/a/b"])

    def test_12_parse_template_paths__w_paths(self):
        self.assertEquals(TT.parse_template_paths("/a/b/c.yml", "/a/d:/a/e"),
                          ["/a/d", "/a/e", "/a/b"])


class Test_10_effectful_functions(unittest.TestCase):
    pass

# vim:sw=4:ts=4:et:
