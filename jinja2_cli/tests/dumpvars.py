import jinja2_cli.dumpvars as D
import unittest
from jinja2 import Environment


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

if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:
