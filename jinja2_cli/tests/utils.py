#
# Copyright (C). 2011, 2012 Satoru SATOH <ssato at redhat.com>
#
import os.path
import os
import unittest

import jinja2_cli.utils as TT
import jinja2_cli.tests.common as C


class Test_00_functions(unittest.TestCase):

    def test_02_uniq(self):
        self.assertEquals(TT.uniq([]), [])
        self.assertEquals(
            TT.uniq([1, 4, 5, 1, 2, 3, 5, 10, 13, 2]),
            [1, 4, 5, 2, 3, 10, 13]
        )

    def test_03_chaincalls(self):
        self.assertEquals(
            TT.chaincalls([lambda x: x + 1, lambda x: x - 1], 1),
            1
        )

    def test_04_normpath(self):
        self.assertEquals(TT.normpath("/tmp/../etc/hosts"), "/etc/hosts")
        self.assertEquals(TT.normpath("~root/t"), "/root/t")

    def test_04_normpath__relative(self):
        curdir = os.curdir
        relpath = "./a/b/c.txt"

        self.assertEquals(TT.normpath(relpath),
                          TT.normpath(os.path.join(curdir, relpath)))

    def test_05_flip(self):
        self.assertEquals(TT.flip((1, 3)), (3, 1))

    def test_06_concat(self):
        self.assertEquals(TT.concat([]), [])
        self.assertEquals(TT.concat(()), [])
        self.assertEquals(TT.concat([[1, 2, 3], [4, 5]]), [1, 2, 3, 4, 5])
        self.assertEquals(
            TT.concat([[1, 2, 3], [4, 5, [6, 7]]]), [1, 2, 3, 4, 5, [6, 7]]
        )
        self.assertEquals(
            TT.concat(((1, 2, 3), (4, 5, [6, 7]))), [1, 2, 3, 4, 5, [6, 7]]
        )
        self.assertEquals(
            TT.concat((i, i * 2) for i in range(3)), [0, 0, 1, 2, 2, 4]
        )

    def test_40_parse_filespec__w_type(self):
        self.assertEquals(TT.parse_filespec("json:a.json"),
                          [("a.json", "json")])

    def test_41_parse_filespec__wo_type(self):
        self.assertEquals(TT.parse_filespec("a.json"), [("a.json", None)])


class Test_10_with_workdir(unittest.TestCase):

    def setUp(self):
        self.workdir = C.setup_workdir()

    def tearDown(self):
        C.cleanup_workdir(self.workdir)

    def test_50_write_to_output__create_dir(self):
        output = os.path.join(self.workdir, "a", "out.txt")
        TT.write_to_output("hello", output)

        self.assertEquals(open(output).read(), "hello")

    def test_52_write_to_output__stdout(self):
        TT.write_to_output("hello")

if __name__ == '__main__':
    unittest.main()

# vim:sw=4:ts=4:et:
