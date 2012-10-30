import jinja2_cui.dumpvars as D
import unittest
from jinja2 import Environment, meta

class Test_dumpvar(unittest.TestCase):
    def test_dumpvars(self):
        tmpl = '{{ a }}{{ b.b0 }}{{ c.c0.c1 + c.c0.c2 + c.c1}}'
        env = Environment()
        ast = env.parse(tmpl)
        self.assertTrue(D.find_attrs(ast, 'a') == [['a']])
        self.assertTrue(D.find_attrs(ast, 'b') == [['b', 'b0']])
        self.assertTrue(D.find_attrs(ast, 'c') == [['c', 'c0', 'c1'],
                                                   ['c', 'c0', 'c2'],
                                                   ['c', 'c1']])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_dumpvar))
    return suite
