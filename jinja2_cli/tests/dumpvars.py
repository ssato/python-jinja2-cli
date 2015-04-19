#
# Copyright (C) 2015 Satoru SATOH <ssato at redhat.com>
#
import jinja2
import unittest

import jinja2_cli.dumpvars as TT


class Test_dumpvar(unittest.TestCase):
    def test_dumpvars(self):
        tmpl = '{{ a }}{{ b.b0 }}{{ c.c0.c1 + c.c0.c2 + c.c1}}'
        env = jinja2.Environment()
        ast = env.parse(tmpl)
        self.assertTrue(TT.find_attrs(ast, 'a') == [['a']])
        self.assertTrue(TT.find_attrs(ast, 'b') == [['b', 'b0']])
        self.assertTrue(TT.find_attrs(ast, 'c') == [['c', 'c0', 'c1'],
                                                    ['c', 'c0', 'c2'],
                                                    ['c', 'c1']])

# vim:sw=4:ts=4:et:
